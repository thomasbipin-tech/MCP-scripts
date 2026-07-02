"""Runtime configuration.

Plain ``os.getenv`` (no pydantic-settings dependency) so the module imports in a
bare interpreter. Defaults are dev-safe: SQLite + offline narrator + local
storage, so the API boots and the smoke test runs with nothing provisioned.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


def _b(name: str, default: bool) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.lower() in ("1", "true", "yes", "on")


@dataclass
class Settings:
    env: str = os.getenv("ENV", "development")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./dealproof.db")
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    jwt_secret: str = os.getenv("JWT_SECRET", "dev-insecure-change-me")
    signed_url_ttl: int = int(os.getenv("SIGNED_URL_TTL_SECONDS", "900"))
    data_retention_days: int = int(os.getenv("DATA_RETENTION_DAYS", "180"))
    magic_link_ttl: int = int(os.getenv("MAGIC_LINK_TTL_SECONDS", "900"))
    s3_endpoint: str = os.getenv("S3_ENDPOINT", "")
    s3_access_key: str = os.getenv("S3_ACCESS_KEY", "")
    s3_secret_key: str = os.getenv("S3_SECRET_KEY", "")
    s3_bucket: str = os.getenv("S3_BUCKET", "dealproof-docs")
    stripe_secret_key: str = os.getenv("STRIPE_SECRET_KEY", "")
    stripe_webhook_secret: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    resend_api_key: str = os.getenv("RESEND_API_KEY", "")
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:8080")

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


settings = Settings()
