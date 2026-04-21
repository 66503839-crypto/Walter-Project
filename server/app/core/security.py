"""JWT 与密码哈希工具。"""
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return _pwd_ctx.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_ctx.verify(plain, hashed)


def create_access_token(
    subject: str | int,
    extra: dict[str, Any] | None = None,
    expires_minutes: int | None = None,
) -> str:
    """签发 Access Token。subject 放 user_id。"""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.jwt_access_ttl_minutes
    )
    payload: dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "typ": "access",
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str | int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_ttl_days)
    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "typ": "refresh",
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token 无效: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
