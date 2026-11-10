"""Application configuration loaded from environment variables.

All secrets and environment-specific values must come from the environment
(or a local .env file). Nothing sensitive is hardcoded here.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings.

    Field names map case-insensitively to environment variables, so
    ``database_url`` is read from ``DATABASE_URL``, and so on.
    """

    database_url: str = Field(..., description="SQLAlchemy database URL")
    jwt_secret_key: str = Field(
        ...,
        min_length=32,
        description="Secret used to sign JWT access tokens",
    )
    jwt_algorithm: Literal["HS256", "HS384", "HS512"] = Field(
        default="HS256",
        description="JWT signing algorithm",
    )
    access_token_expire_minutes: int = Field(
        default=30,
        gt=0,
        le=60 * 24 * 30,
        description="Access token lifetime in minutes",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("jwt_secret_key")
    @classmethod
    def reject_placeholder_secret(cls, value: str) -> str:
        """Refuse to start with the example/placeholder secret."""

        lowered = value.strip().lower()
        if lowered.startswith(
            ("replace-with", "changeme", "change-me", "your-secret")
        ):
            raise ValueError(
                "JWT_SECRET_KEY is still a placeholder. Generate a strong "
                "random value for your .env file."
            )
        return value


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""

    return Settings()


settings = get_settings()
