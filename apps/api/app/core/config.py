"""Configuration settings for the VibeCheck API."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

# Guest user constants (used when DEV_AUTH_BYPASS=true)
GUEST_USER_ID = "00000000-0000-0000-0000-000000000000"
GUEST_USER_EMAIL = "guest@vibecheck.dev"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database settings
    database_host: str = "localhost"
    database_port: int = 5432
    database_user: str = "postgres"
    database_password: str = "postgres"
    database_name: str = "vibecheck"

    # Redis settings
    redis_url: str | None = None  # Full Redis URL (takes precedence)
    redis_host: str = "localhost"
    redis_port: int = 6379

    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False

    # Authentication settings (legacy - kept for backward compatibility)
    secret_key: str = "CHANGE-THIS-IN-PRODUCTION"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Clerk authentication settings
    clerk_issuer: str = ""  # e.g., https://your-app.clerk.accounts.dev
    clerk_jwks_url: str = ""  # e.g., https://your-app.clerk.accounts.dev/.well-known/jwks.json

    # AWS S3 settings
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    s3_bucket_name: str = ""

    # Development settings
    dev_auth_bypass: bool = False

    # Database SSL settings (required for Neon)
    database_sslmode: str = "require"

    @property
    def database_url(self) -> str:
        """Construct PostgreSQL database URL."""
        base_url = (
            f"postgresql://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )
        # Add SSL mode for cloud databases like Neon
        if self.database_sslmode:
            return f"{base_url}?sslmode={self.database_sslmode}"
        return base_url

    def get_redis_url(self) -> str:
        """Get Redis URL (use redis_url if set, otherwise construct from host/port)."""
        url = self.redis_url if self.redis_url else f"redis://{self.redis_host}:{self.redis_port}/0"

        # Celery requires ssl_cert_reqs parameter for SSL Redis connections
        if url.startswith("rediss://") and "ssl_cert_reqs" not in url:
            separator = "&" if "?" in url else "?"
            url += f"{separator}ssl_cert_reqs=CERT_NONE"

        return url


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
