"""Unit tests for configuration module."""

import os
from unittest.mock import patch

import pytest


class TestConfigLoading:
    """Tests for configuration loading from environment."""

    def test_config_loading(self):
        """Config loads required environment variables."""
        with patch.dict(os.environ, {
            "DATABASE_HOST": "testhost",
            "DATABASE_PORT": "5432",
            "DATABASE_USER": "testuser",
            "DATABASE_PASSWORD": "testpass",
            "DATABASE_NAME": "testdb",
            "REDIS_HOST": "redishost",
            "REDIS_PORT": "6379",
        }):
            from app.core.config import get_settings

            # Clear cache to pick up new environment variables
            get_settings.cache_clear()
            settings = get_settings()

            assert settings.database_host == "testhost"
            assert settings.database_port == 5432
            assert settings.database_user == "testuser"
            assert settings.database_password == "testpass"
            assert settings.database_name == "testdb"

    def test_config_defaults(self):
        """Config uses defaults for optional variables."""
        with patch.dict(os.environ, {
            "DATABASE_HOST": "localhost",
            "DATABASE_PORT": "5432",
            "DATABASE_USER": "postgres",
            "DATABASE_PASSWORD": "postgres",
            "DATABASE_NAME": "vibecheck",
            "REDIS_HOST": "localhost",
            "REDIS_PORT": "6379",
        }, clear=True):
            from app.core.config import Settings

            settings = Settings()

            assert settings.debug is False
            assert settings.api_host == "0.0.0.0"
            assert settings.api_port == 8000


class TestDatabaseUrl:
    """Tests for database URL construction."""

    def test_config_database_url(self):
        """Database URL is constructed correctly from components."""
        with patch.dict(os.environ, {
            "DATABASE_HOST": "myhost",
            "DATABASE_PORT": "5432",
            "DATABASE_USER": "myuser",
            "DATABASE_PASSWORD": "mypass",
            "DATABASE_NAME": "mydb",
            "REDIS_HOST": "localhost",
            "REDIS_PORT": "6379",
        }):
            from app.core.config import Settings

            settings = Settings()

            assert settings.database_url == "postgresql://myuser:mypass@myhost:5432/mydb"


class TestRedisUrl:
    """Tests for Redis URL construction."""

    def test_config_redis_url(self):
        """Redis URL is constructed correctly from components."""
        with patch.dict(os.environ, {
            "DATABASE_HOST": "localhost",
            "DATABASE_PORT": "5432",
            "DATABASE_USER": "postgres",
            "DATABASE_PASSWORD": "postgres",
            "DATABASE_NAME": "vibecheck",
            "REDIS_HOST": "myredis",
            "REDIS_PORT": "6380",
        }):
            from app.core.config import Settings

            settings = Settings()

            assert settings.redis_url == "redis://myredis:6380/0"
