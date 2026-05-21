"""
Fungsi-fungsi keamanan:
  - hash_password / verify_password  (bcrypt via passlib)
  - create_access_token / decode_access_token  (JWT HS256 via python-jose)
"""
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.models.user import UserRole


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------- Password ----------------
def hash_password(plain_password: str) -> str:
    """Hash password dengan bcrypt (one-way)."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Bandingkan password plaintext dengan hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ---------------- JWT ----------------
def create_access_token(user_id: int, role: UserRole, expires_delta: timedelta | None = None) -> str:
    """Buat JWT access token untuk user."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "role": role.value,
        "exp": expire,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_password_reset_token(
    user_id: int,
    role: UserRole,
    expires_delta: timedelta | None = None,
) -> str:
    """Buat JWT token khusus reset password."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.password_reset_token_expire_minutes)
    )
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "role": role.value,
        "purpose": "password_reset",
        "exp": expire,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode JWT. Raise ValueError jika invalid/expired."""
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError as e:
        raise ValueError(f"Token tidak valid: {e}") from e


def decode_password_reset_token(token: str) -> dict[str, Any]:
    """Decode token reset password dan pastikan purpose-nya benar."""
    payload = decode_access_token(token)
    if payload.get("purpose") != "password_reset":
        raise ValueError("Token reset password tidak valid")
    return payload
