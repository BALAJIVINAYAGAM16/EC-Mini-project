import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta

import bcrypt
from jose import jwt

from app.core.config import ALGORITHM, SECRET_KEY


PBKDF2_ITERATIONS = 390000
PBKDF2_SCHEME = "pbkdf2_sha256"


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=2)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("utf-8")


def _b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value.encode("utf-8"))


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return (
        f"{PBKDF2_SCHEME}$"
        f"{PBKDF2_ITERATIONS}$"
        f"{_b64encode(salt)}$"
        f"{_b64encode(derived_key)}"
    )


def _verify_pbkdf2(password: str, hashed: str) -> bool:
    try:
        scheme, iterations, salt, expected_hash = hashed.split("$", 3)
    except ValueError:
        return False

    if scheme != PBKDF2_SCHEME:
        return False

    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        _b64decode(salt),
        int(iterations),
    )
    return hmac.compare_digest(_b64encode(derived_key), expected_hash)


def _verify_legacy_bcrypt(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def verify_password(password: str, hashed: str) -> bool:
    if hashed.startswith(f"{PBKDF2_SCHEME}$"):
        return _verify_pbkdf2(password, hashed)

    if hashed.startswith("$2a$") or hashed.startswith("$2b$") or hashed.startswith("$2y$"):
        return _verify_legacy_bcrypt(password, hashed)

    return False
