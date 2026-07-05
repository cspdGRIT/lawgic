import hashlib
import hmac
from datetime import datetime, timezone, timedelta

import razorpay
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.subscription import (
    Subscription, Payment,
    PLAN_FREE, PLAN_PRO, PLAN_FIRM,
    PLAN_PRICE_INR, PLAN_LIMITS,
)

router = APIRouter()

PLANS_META = [
    {
        "id": PLAN_FREE,
        "name": "Free",
        "price_inr": 0,
        "price_paise": 0,
        "billing": "forever",
        "tagline": "Get started",
        "features": [
            "10 AI queries/month",
            "3 cases",
            "5 document drafts",
            "5 legal research searches",
            "Community support",
        ],
        "limits": PLAN_LIMITS[PLAN_FREE],
        "popular": False,
    },
    {
        "id": PLAN_PRO,
        "name": "Pro",
        "price_inr": 499,
        "price_paise": PLAN_PRICE_INR[PLAN_PRO],
        "billing": "per month",
        "tagline": "For individuals & freelancers",
        "features": [
            "500 AI queries/month",
            "50 cases",
            "100 document drafts",
            "100 legal research searches",
            "Priority support",
            "Indian Kanoon case search",
            "Multi-language documents",
        ],
        "limits": PLAN_LIMITS[PLAN_PRO],
        "popular": True,
    },
    {
        "id": PLAN_FIRM,
        "name": "Firm",
        "price_inr": 1999,
        "price_paise": PLAN_PRICE_INR[PLAN_FIRM],
        "billing": "per month",
        "tagline": "For law firms & enterprises",
        "features": [
            "Unlimited AI queries",
            "Unlimited cases",
            "Unlimited documents",
            "Unlimited research",
            "Dedicated support",
            "Team management (coming soon)",
            "Custom branding (coming soon)",
            "API access (coming soon)",
        ],
        "limits": PLAN_LIMITS[PLAN_FIRM],
        "popular": False,
    },
]


def _razorpay_client():
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        raise HTTPException(status_code=501, detail="Razorpay not configured")
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


async def _get_or_create_subscription(user_id: int, db: AsyncSession) -> Subscription:
    result = await db.execute(select(Subscription).where(Subscription.user_id == user_id))
    sub = result.scalar_one_or_none()
    if not sub:
        sub = Subscription(user_id=user_id, plan=PLAN_FREE, status="active")
        db.add(sub)
        await db.flush()
        await db.refresh(sub)
    return sub


# ── Public ────────────────────────────────────────────────────────────────────

@router.get("/plans")
async def list_plans():
    return {"plans": PLANS_META}


# ── Authenticated ─────────────────────────────────────────────────────────────

@router.get("/subscription")
async def get_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sub = await _get_or_create_subscription(current_user.id, db)
    plan_meta = next((p for p in PLANS_META if p["id"] == sub.plan), PLANS_META[0])
    return {
        "plan": sub.plan,
        "status": sub.status,
        "current_period_end": sub.current_period_end,
        "limits": plan_meta["limits"],
        "razorpay_key_id": settings.RAZORPAY_KEY_ID or None,
    }


class CreateOrderRequest(BaseModel):
    plan: str  # "pro" or "firm"


@router.post("/create-order")
async def create_order(
    req: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if req.plan not in (PLAN_PRO, PLAN_FIRM):
        raise HTTPException(status_code=400, detail="Invalid plan")

    amount = PLAN_PRICE_INR[req.plan]
    client = _razorpay_client()
    order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "notes": {"user_id": str(current_user.id), "plan": req.plan},
    })

    payment = Payment(
        user_id=current_user.id,
        razorpay_order_id=order["id"],
        plan=req.plan,
        amount_paise=amount,
        status="created",
    )
    db.add(payment)
    await db.flush()

    return {
        "order_id": order["id"],
        "amount": amount,
        "currency": "INR",
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "name": "Lawgic",
        "description": f"Lawgic {req.plan.title()} Plan — Monthly",
        "prefill": {
            "name": current_user.full_name,
            "email": current_user.email,
            "contact": current_user.phone or "",
        },
    }


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


@router.post("/verify")
async def verify_payment(
    req: VerifyPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify HMAC signature
    expected = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        f"{req.razorpay_order_id}|{req.razorpay_payment_id}".encode(),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected, req.razorpay_signature):
        raise HTTPException(status_code=400, detail="Invalid payment signature")

    # Fetch the payment record
    result = await db.execute(
        select(Payment).where(Payment.razorpay_order_id == req.razorpay_order_id)
    )
    payment = result.scalar_one_or_none()
    if not payment or payment.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Order not found")

    payment.razorpay_payment_id = req.razorpay_payment_id
    payment.razorpay_signature = req.razorpay_signature
    payment.status = "paid"

    # Upgrade subscription
    sub = await _get_or_create_subscription(current_user.id, db)
    sub.plan = payment.plan
    sub.status = "active"
    now = datetime.now(timezone.utc)
    sub.current_period_start = now
    sub.current_period_end = now + timedelta(days=30)

    await db.flush()
    return {"success": True, "plan": sub.plan, "valid_until": sub.current_period_end}


@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sub = await _get_or_create_subscription(current_user.id, db)
    if sub.plan == PLAN_FREE:
        raise HTTPException(status_code=400, detail="No active paid subscription")
    sub.status = "cancelled"
    await db.flush()
    return {"success": True, "message": "Subscription cancelled. Access continues until period end."}
