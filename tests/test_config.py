"""Configuration validation tests."""

import pytest
from pydantic import ValidationError

from config import Settings

VALID_SETTINGS = {
    "database_url": "sqlite+pysqlite:///:memory:",
    "jwt_secret_key": "x" * 48,
}


def test_valid_settings_load():
    settings = Settings(**VALID_SETTINGS)

    assert settings.jwt_algorithm == "HS256"
    assert settings.access_token_expire_minutes == 30


def test_short_jwt_secret_is_rejected():
    with pytest.raises(ValidationError):
        Settings(
            database_url=VALID_SETTINGS["database_url"],
            jwt_secret_key="too-short",
        )


def test_placeholder_jwt_secret_is_rejected():
    with pytest.raises(ValidationError):
        Settings(
            database_url=VALID_SETTINGS["database_url"],
            jwt_secret_key=(
                "replace-with-a-long-random-secret-at-least-32-characters"
            ),
        )


def test_unsafe_jwt_algorithm_is_rejected():
    with pytest.raises(ValidationError):
        Settings(**VALID_SETTINGS, jwt_algorithm="none")
