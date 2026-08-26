from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class AccessStatusResponse(BaseModel):
    access_status: str
    credit_balance: int
    latest_request: Optional["AccessRequestResponse"] = None


class PaymentInfoResponse(BaseModel):
    upi_id: str
    payee_name: str
    pack: str
    credits: int
    amount_rupees: int
    upi_uri: str
    qr_data_uri: str  # data:image/png;base64,... — render directly in an <img src>


class SubmitAccessRequestBody(BaseModel):
    pack: str = "starter"  # key into CREDIT_PACKS (services/upi.py)
    utr_reference: Optional[str] = None
    note: Optional[str] = None


class AccessRequestResponse(BaseModel):
    id: int
    user_id: int
    status: str
    amount_rupees: int
    credits: int
    utr_reference: Optional[str] = None
    note: Optional[str] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AccessRequestWithUser(AccessRequestResponse):
    user_email: str
    user_full_name: str


AccessStatusResponse.model_rebuild()
