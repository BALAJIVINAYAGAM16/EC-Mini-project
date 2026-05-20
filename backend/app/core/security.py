from datetime import datetime, timedelta, timezone
import hashlib
import secrets
import bcrypt
from jose import jwt
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, REFRESH_TOKEN_EXPIRE_DAYS, SECRET_KEY


BCRYPT_MAX_PASSWORD_BYTES = 72


def is_valid_bcrypt_password(password: str) -> bool:
    return len(password.encode("utf-8")) <= BCRYPT_MAX_PASSWORD_BYTES


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token() -> tuple[str, datetime]:
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    return secrets.token_urlsafe(48), expires_at.replace(tzinfo=None)


def create_password_reset_token(expires_minutes: int) -> tuple[str, datetime]:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    return secrets.token_urlsafe(32), expires_at.replace(tzinfo=None)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def hash_password(password: str):
    if not is_valid_bcrypt_password(password):
        raise ValueError("Password cannot be longer than 72 bytes")
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str):
    if not is_valid_bcrypt_password(password):
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except (TypeError, ValueError):
        return False
