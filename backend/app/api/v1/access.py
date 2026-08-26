from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.access import require_admin
from app.core.config import settings
from app.core.credits import CREDIT_PACKS, grant_credits
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.access_request import AccessRequest
from app.models.user import User
from app.schemas.access import (
    AccessRequestResponse,
    AccessRequestWithUser,
    AccessStatusResponse,
    PaymentInfoResponse,
    SubmitAccessRequestBody,
)
from app.services.upi import build_qr_data_uri, build_upi_uri

router = APIRouter()


# ── User-facing: check status, get payment info, submit a request ────────────────
# None of these require require_quota_or_credit — you have to be able to reach the
# purchase flow itself before you have anything to spend.

@router.get("/packs")
async def list_credit_packs():
    return CREDIT_PACKS


@router.get("/status", response_model=AccessStatusResponse)
async def get_access_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AccessRequest)
        .where(AccessRequest.user_id == current_user.id)
        .order_by(AccessRequest.created_at.desc())
        .limit(1)
    )
    latest = result.scalar_one_or_none()
    return AccessStatusResponse(
        access_status=current_user.access_status,
        credit_balance=current_user.credit_balance,
        latest_request=AccessRequestResponse.model_validate(latest) if latest else None,
    )


@router.get("/payment-info", response_model=PaymentInfoResponse)
async def get_payment_info(
    pack: str = Query(default="starter"),
    current_user: User = Depends(get_current_user),
):
    if not settings.UPI_VPA:
        raise HTTPException(status_code=501, detail="Payment collection isn't configured yet — set UPI_VPA.")
    if pack not in CREDIT_PACKS:
        raise HTTPException(status_code=400, detail=f"Unknown pack '{pack}'. Choose one of: {list(CREDIT_PACKS)}")

    chosen = CREDIT_PACKS[pack]
    note = f"Lawgic {pack} pack user {current_user.id}"
    uri = build_upi_uri(note, chosen["price_rupees"])
    return PaymentInfoResponse(
        upi_id=settings.UPI_VPA,
        payee_name=settings.UPI_PAYEE_NAME,
        pack=pack,
        credits=chosen["credits"],
        amount_rupees=chosen["price_rupees"],
        upi_uri=uri,
        qr_data_uri=build_qr_data_uri(uri),
    )


@router.post("/requests", response_model=AccessRequestResponse, status_code=status.HTTP_201_CREATED)
async def submit_access_request(
    body: SubmitAccessRequestBody,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.access_status == "approved":
        raise HTTPException(status_code=400, detail="Your account already has unlimited legacy access.")
    if body.pack not in CREDIT_PACKS:
        raise HTTPException(status_code=400, detail=f"Unknown pack '{body.pack}'. Choose one of: {list(CREDIT_PACKS)}")

    result = await db.execute(
        select(AccessRequest).where(
            AccessRequest.user_id == current_user.id, AccessRequest.status == "pending"
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="You already have a request pending review.")

    chosen = CREDIT_PACKS[body.pack]
    req = AccessRequest(
        user_id=current_user.id,
        amount_rupees=chosen["price_rupees"],
        credits=chosen["credits"],
        utr_reference=body.utr_reference,
        note=body.note,
    )
    db.add(req)
    await db.flush()
    await db.refresh(req)
    return req


# ── Admin: review queue ───────────────────────────────────────────────────────────

@router.get("/admin/requests", response_model=list[AccessRequestWithUser])
async def list_access_requests(
    request_status: Optional[str] = Query(default="pending", alias="status"),
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(AccessRequest, User).join(User, AccessRequest.user_id == User.id)
    if request_status:
        query = query.where(AccessRequest.status == request_status)
    query = query.order_by(AccessRequest.created_at.desc())
    result = await db.execute(query)

    out = []
    for req, user in result.all():
        out.append(
            AccessRequestWithUser(
                **AccessRequestResponse.model_validate(req).model_dump(),
                user_email=user.email,
                user_full_name=user.full_name,
            )
        )
    return out


@router.post("/admin/requests/{request_id}/approve", response_model=AccessRequestResponse)
async def approve_access_request(
    request_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(AccessRequest).where(AccessRequest.id == request_id))
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    if req.status != "pending":
        raise HTTPException(status_code=400, detail=f"Request already {req.status}")

    # Conditional UPDATE, not read-check-then-write — two concurrent approve calls for
    # the same request (two admin tabs, a retried request) could otherwise both read
    # status=="pending" and both grant credits, double-crediting the user. Only the
    # request that actually flips pending -> approved here proceeds to grant credits.
    now = datetime.now(timezone.utc)
    update_result = await db.execute(
        update(AccessRequest)
        .where(AccessRequest.id == request_id, AccessRequest.status == "pending")
        .values(status="approved", reviewed_by_user_id=admin.id, reviewed_at=now)
    )
    if update_result.rowcount == 0:
        raise HTTPException(status_code=400, detail="Request already reviewed")

    user_result = await db.execute(select(User).where(User.id == req.user_id))
    user = user_result.scalar_one_or_none()
    if user:
        await grant_credits(user, req.credits, reason="purchase", db=db)

    await db.flush()
    await db.refresh(req)
    return req


@router.post("/admin/requests/{request_id}/reject", response_model=AccessRequestResponse)
async def reject_access_request(
    request_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(AccessRequest).where(AccessRequest.id == request_id))
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    if req.status != "pending":
        raise HTTPException(status_code=400, detail=f"Request already {req.status}")

    req.status = "rejected"
    req.reviewed_by_user_id = admin.id
    req.reviewed_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(req)
    return req
