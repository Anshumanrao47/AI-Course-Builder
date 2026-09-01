"""
Password hashing and JWT helpers.

Uses the `bcrypt` package directly rather than passlib: passlib is
unmaintained and breaks on bcrypt >= 4.1 (it probes an internal attribute
bcrypt no longer exposes). Bcrypt itself only hashes the first 72 bytes of
a password, so input length is capped in the Pydantic schema.
"""
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT for the given subject (typically the user id)."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> str | None:
    """Return the subject (user id) encoded in a valid token, or None if invalid/expired."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


def create_signed_payload_token(payload: dict, expires_minutes: int = 30) -> str:
    """
    Sign an arbitrary payload dict as a short-lived JWT. Used to hold
    server-generated data (e.g. assessment questions + correct answers)
    across two requests without a dedicated DB table for it.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode = {**payload, "exp": expire}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_signed_payload_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
