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
    redis_host: str = "localhost"
    redis_port: int = 6379

    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False

    # Authentication settings
    secret_key: str = "CHANGE-THIS-IN-PRODUCTION"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # AWS S3 settings
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    s3_bucket_name: str = ""

    # Development settings
    dev_auth_bypass: bool = False

    @property
    def database_url(self) -> str:
        """Construct PostgreSQL database URL."""
        return (
            f"postgresql://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )

    @property
    def redis_url(self) -> str:
        """Construct Redis URL."""
        return f"redis://{self.redis_host}:{self.redis_port}/0"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
