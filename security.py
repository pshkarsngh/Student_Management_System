"""Password hashing and JWT helpers.

Authentication primitives live here so that routing code stays focused on
HTTP concerns. Passwords are hashed with Argon2 via pwdlib.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from config import settings

# Argon2 is the recommended default used by pwdlib.
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a plaintext password using Argon2."""

    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True when the plaintext password matches the stored hash."""

    try:
        return password_hash.verify(plain_password, hashed_password)
    except Exception:
        # A malformed/legacy hash must never crash the login endpoint.
        return False


def create_access_token(
    subject: str | int,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token for the given subject."""

    now = datetime.now(timezone.utc)
    expires_at = now + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.access_token_expire_minutes)
    )

    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT access token.

    Raises ``jwt.exceptions.InvalidTokenError`` when the token is malformed,
    tampered with, or expired.
    """

    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
        options={"require": ["exp", "sub"]},
    )


__all__ = [
    "InvalidTokenError",
    "create_access_token",
    "decode_access_token",
    "hash_password",
    "verify_password",
]
