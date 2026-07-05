import secrets
from datetime import timedelta

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    REFRESH_COOKIE,
    create_access_token,
    create_refresh_token_record,
    get_current_user,
    hash_password,
    refresh_cookie_kwargs,
    revoke_all_refresh_tokens,
    rotate_refresh_token,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter()


class GoogleAuthRequest(BaseModel):
    token: str


# ── helpers ───────────────────────────────────────────────────────────────────

def _access_token(user_id: int) -> str:
    return create_access_token(
        data={"sub": str(user_id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


async def _auth_response(user: User, response: Response, db: AsyncSession) -> TokenResponse:
    access = _access_token(user.id)
    refresh_raw = await create_refresh_token_record(user.id, db)
    response.set_cookie(**refresh_cookie_kwargs(refresh_raw))
    return TokenResponse(access_token=access, user=UserResponse.model_validate(user))


# ── Register ──────────────────────────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, response: Response, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        full_name=request.full_name,
        phone=request.phone,
        user_type=request.user_type,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return await _auth_response(user, response, db)


# ── Login ─────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is deactivated")

    return await _auth_response(user, response, db)


# ── Refresh ───────────────────────────────────────────────────────────────────

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    response: Response,
    refresh: str | None = Cookie(default=None, alias=REFRESH_COOKIE),
    db: AsyncSession = Depends(get_db),
):
    if not refresh:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")

    new_raw, user_id = await rotate_refresh_token(refresh, db)

    from app.models.user import User
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    access = _access_token(user.id)
    response.set_cookie(**refresh_cookie_kwargs(new_raw))
    return TokenResponse(access_token=access, user=UserResponse.model_validate(user))


# ── Logout ────────────────────────────────────────────────────────────────────

@router.post("/logout")
async def logout(
    response: Response,
    refresh: str | None = Cookie(default=None, alias=REFRESH_COOKIE),
    db: AsyncSession = Depends(get_db),
):
    if refresh:
        try:
            from app.models.token import RefreshToken
            from app.core.security import hash_refresh_token
            h = hash_refresh_token(refresh)
            result = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == h))
            rec = result.scalar_one_or_none()
            if rec:
                rec.revoked = True
                await db.flush()
        except Exception:
            pass
    response.set_cookie(**refresh_cookie_kwargs("", clear=True))
    return {"success": True}


# ── Me ────────────────────────────────────────────────────────────────────────

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


# ── Google OAuth ──────────────────────────────────────────────────────────────

@router.post("/google", response_model=TokenResponse)
async def google_auth(request: GoogleAuthRequest, response: Response, db: AsyncSession = Depends(get_db)):
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=501, detail="Google OAuth not configured")
    try:
        from google.auth.transport import requests as google_requests
        from google.oauth2 import id_token
        id_info = id_token.verify_oauth2_token(
            request.token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    email = id_info.get("email", "")
    full_name = id_info.get("name", email.split("@")[0])

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        user = User(
            email=email,
            password_hash=hash_password(secrets.token_urlsafe(32)),
            full_name=full_name,
            user_type="client",
            is_active=True,
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)

    return await _auth_response(user, response, db)
