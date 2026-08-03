import json
from functools import lru_cache
from typing import Any
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application settings and environment variables manager for WorkMate AI."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application Info & Runtime
    APP_NAME: str = "WorkMate AI API"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = Field("dev", description="Application environment: dev, staging, prod")
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # CORS & Security Boundaries
    ALLOWED_ORIGINS: list[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins list or comma-separated string",
    )

    # Logging Configuration
    LOG_LEVEL: str = Field("INFO", description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Snowflake Connection Settings
    SNOWFLAKE_ACCOUNT: str = Field(..., description="Snowflake account identifier")
    SNOWFLAKE_USER: str = Field(..., description="Snowflake username")
    SNOWFLAKE_PASSWORD: str = Field(..., description="Snowflake password")
    SNOWFLAKE_WAREHOUSE: str = Field(..., description="Snowflake warehouse name")
    SNOWFLAKE_DATABASE: str = Field(..., description="Snowflake database name")
    SNOWFLAKE_SCHEMA: str = Field("PUBLIC", description="Snowflake schema name")
    SNOWFLAKE_ROLE: str | None = Field(None, description="Snowflake user role (optional)")

    # Auth & Security Credentials
    JWT_SECRET: str = Field(..., description="Secret key used for signing JWT tokens")
    JWT_ALGORITHM: str = Field("HS256", description="JWT signature algorithm")
    JWT_ACCESS_EXPIRE_MINUTES: int = Field(60, description="Access token expiration in minutes")
    JWT_REFRESH_EXPIRE_DAYS: int = Field(7, description="Refresh token expiration in days")

    # Orchestration Settings
    N8N_WEBHOOK_BASE_URL: str = Field(..., description="Base URL for n8n webhook triggers")

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        return [str(item).strip() for item in parsed]
                except json.JSONDecodeError:
                    pass
            return [item.strip() for item in v.split(",") if item.strip()]
        elif isinstance(v, list):
            return [str(item).strip() for item in v]
        raise ValueError("ALLOWED_ORIGINS must be a list or a comma-separated string")


@lru_cache
def get_settings() -> Settings:
    """Read and cache application settings."""
    return Settings()


# Export cached singleton instance alongside factory function
settings: Settings = get_settings()

