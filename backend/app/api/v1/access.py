from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.access import require_admin
from app.core.config import settings
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
# None of these require require_approved_access — a pending user has to be able to
# reach them, that's the whole point.

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
        latest_request=AccessRequestResponse.model_validate(latest) if latest else None,
    )


@router.get("/payment-info", response_model=PaymentInfoResponse)
async def get_payment_info(current_user: User = Depends(get_current_user)):
    if not settings.UPI_VPA:
        raise HTTPException(status_code=501, detail="Payment collection isn't configured yet — set UPI_VPA.")
    note = f"Lawgic access {current_user.id}"
    uri = build_upi_uri(note)
    return PaymentInfoResponse(
        upi_id=settings.UPI_VPA,
        payee_name=settings.UPI_PAYEE_NAME,
        amount_rupees=settings.ACCESS_FEE_RUPEES,
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
        raise HTTPException(status_code=400, detail="Your account is already approved.")

    result = await db.execute(
        select(AccessRequest).where(
            AccessRequest.user_id == current_user.id, AccessRequest.status == "pending"
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="You already have a request pending review.")

    req = AccessRequest(
        user_id=current_user.id,
        amount_rupees=settings.ACCESS_FEE_RUPEES,
        utr_reference=body.utr_reference,
        note=body.note,
    )
    db.add(req)
    current_user.access_status = "pending"
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


async def _review(request_id: int, new_status: str, admin: User, db: AsyncSession) -> AccessRequest:
    result = await db.execute(select(AccessRequest).where(AccessRequest.id == request_id))
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    if req.status != "pending":
        raise HTTPException(status_code=400, detail=f"Request already {req.status}")

    req.status = new_status
    req.reviewed_by_user_id = admin.id
    req.reviewed_at = datetime.now(timezone.utc)

    user_result = await db.execute(select(User).where(User.id == req.user_id))
    user = user_result.scalar_one_or_none()
    if user:
        user.access_status = new_status  # "approved" or "rejected"

    await db.flush()
    await db.refresh(req)
    return req


@router.post("/admin/requests/{request_id}/approve", response_model=AccessRequestResponse)
async def approve_access_request(
    request_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await _review(request_id, "approved", admin, db)


@router.post("/admin/requests/{request_id}/reject", response_model=AccessRequestResponse)
async def reject_access_request(
    request_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await _review(request_id, "rejected", admin, db)
