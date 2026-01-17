"""Configuration settings for the VibeCheck API."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


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
