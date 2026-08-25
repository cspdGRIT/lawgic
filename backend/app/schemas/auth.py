from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    user_type: str = "client"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "securepass123",
                "full_name": "Rajesh Kumar",
                "phone": "+91-9876543210",
                "user_type": "client",
            }
        }
    )

    def model_post_init(self, __context):
        if len(self.password) < 8:
            raise ValueError("Password must be at least 8 characters")
        # "admin" is deliberately excluded — self-registering as admin would bypass
        # the access-approval gate entirely. Admin accounts are promoted manually.
        if self.user_type not in ("client", "lawyer"):
            raise ValueError("user_type must be one of: client, lawyer")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class OTPRequestBody(BaseModel):
    phone: str


class OTPVerifyBody(BaseModel):
    phone: str
    otp: str
    full_name: Optional[str] = None  # only used the first time this phone registers


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone: Optional[str] = None
    user_type: str
    is_active: bool
    access_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
