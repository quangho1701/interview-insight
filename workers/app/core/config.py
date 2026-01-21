"""Configuration settings for the VibeCheck Worker."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Worker settings loaded from environment variables."""

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

    # S3/MinIO settings
    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket_name: str = "vibecheck-uploads"
    s3_region: str = "us-east-1"

    @property
    def database_url(self) -> str:
        """Construct PostgreSQL database URL."""
        return (
            f"postgresql://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )

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
