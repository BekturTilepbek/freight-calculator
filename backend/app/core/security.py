from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import jwt, JWTError

from app.core.config import settings


def hash_password(plain: str) -> str:
    """
    Хеширует пароль через bcrypt.

    bcrypt имеет жесткий лимит в 72 байта — обрезаем явно,
    чтобы не падать на длинных паролях с кириллицей (где 1 символ = 2 байта в UTF-8).
    """
    pwd_bytes = plain.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    pwd_bytes = plain.encode("utf-8")[:72]
    try:
        return bcrypt.checkpw(pwd_bytes, hashed.encode("utf-8"))
    except ValueError:
        # Хеш в БД битый/неправильного формата
        return False


def create_access_token(subject: str | int, expires_minutes: int | None = None) -> str:
    """JWT-токен. subject — обычно user_id, кладется в claim 'sub'."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.JWT_EXPIRE_MINUTES
    )
    payload = {"sub": str(subject), "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None