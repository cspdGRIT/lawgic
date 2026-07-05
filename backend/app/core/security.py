import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Cookie, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)


# ── Password helpers ──────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ── Access token (15-minute JWT) ──────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# ── Refresh token (opaque, stored hashed in DB) ───────────────────────────────

def generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


async def create_refresh_token_record(user_id: int, db: AsyncSession) -> str:
    from app.models.token import RefreshToken
    raw = generate_refresh_token()
    record = RefreshToken(
        user_id=user_id,
        token_hash=hash_refresh_token(raw),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(record)
    await db.flush()
    return raw


async def rotate_refresh_token(old_raw: str, db: AsyncSession) -> tuple[str, int]:
    """Revoke old refresh token, issue a new one. Returns (new_raw_token, user_id)."""
    from app.models.token import RefreshToken
    old_hash = hash_refresh_token(old_raw)
    result = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == old_hash))
    record = result.scalar_one_or_none()

    if not record or record.revoked or record.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    # Revoke old
    record.revoked = True
    user_id = record.user_id
    await db.flush()

    # Issue new
    new_raw = await create_refresh_token_record(user_id, db)
    return new_raw, user_id


async def revoke_all_refresh_tokens(user_id: int, db: AsyncSession) -> None:
    from app.models.token import RefreshToken
    from sqlalchemy import update
    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked == False)  # noqa: E712
        .values(revoked=True)
    )


# ── get_current_user — reads Bearer token from Authorization header ───────────

def _decode_access_token(token: str) -> int:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "access":
            raise credentials_exception
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return int(user_id)
    except JWTError:
        raise credentials_exception


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    from app.models.user import User

    token: Optional[str] = None
    if credentials:
        token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = _decode_access_token(token)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def get_current_user_from_token(token: str, db: AsyncSession):
    """For WebSocket auth (token passed as query param)."""
    from app.models.user import User
    user_id = _decode_access_token(token)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


# ── Refresh cookie helpers ────────────────────────────────────────────────────

REFRESH_COOKIE = "lawgic_refresh"

def refresh_cookie_kwargs(value: str, clear: bool = False) -> dict:
    is_dev = settings.ENVIRONMENT == "development"
    base = dict(
        key=REFRESH_COOKIE,
        value=value,
        httponly=True,
        # "none" required for cross-domain (Vercel frontend ↔ Render backend)
        # "lax" is fine only when both are on the same domain
        samesite="lax" if is_dev else "none",
        secure=not is_dev,  # "none" requires Secure=True (HTTPS)
        path="/api/v1/auth",
    )
    if clear:
        base["max_age"] = 0
    else:
        base["max_age"] = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
    return base
