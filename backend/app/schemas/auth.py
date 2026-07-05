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
        if self.user_type not in ("client", "lawyer", "admin"):
            raise ValueError("user_type must be one of: client, lawyer, admin")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone: Optional[str] = None
    user_type: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
