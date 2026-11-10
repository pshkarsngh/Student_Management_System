"""Unit tests for password hashing and JWT helpers."""

from datetime import timedelta

import pytest

from security import (
    InvalidTokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_is_hashed_and_verifies():
    password = "mysecret123"
    hashed = hash_password(password)

    assert hashed != password
    assert hashed.startswith("$argon2")
    assert verify_password(password, hashed) is True


def test_wrong_password_is_rejected():
    hashed = hash_password("mysecret123")

    assert verify_password("wrong123", hashed) is False


def test_malformed_hash_is_rejected_without_raising():
    assert verify_password("anything", "not-a-valid-hash") is False


def test_access_token_can_be_created_and_decoded():
    token = create_access_token(subject=42)
    payload = decode_access_token(token)

    assert payload["sub"] == "42"
    assert "exp" in payload
    assert "iat" in payload


def test_expired_token_is_rejected():
    token = create_access_token(
        subject=1,
        expires_delta=timedelta(seconds=-1),
    )

    with pytest.raises(InvalidTokenError):
        decode_access_token(token)


def test_tampered_token_is_rejected():
    token = create_access_token(subject=1)

    with pytest.raises(InvalidTokenError):
        decode_access_token(token + "tampered")
