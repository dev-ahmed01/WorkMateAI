# Pydantic Settings reading environment configuration variables

from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Snowflake Persistence & AI Services Connection Settings
    SNOWFLAKE_ACCOUNT: str = Field(..., env="SNOWFLAKE_ACCOUNT")
    SNOWFLAKE_USER: str = Field(..., env="SNOWFLAKE_USER")
    SNOWFLAKE_PASSWORD: str = Field(..., env="SNOWFLAKE_PASSWORD")
    SNOWFLAKE_WAREHOUSE: str = Field(..., env="SNOWFLAKE_WAREHOUSE")
    SNOWFLAKE_DATABASE: str = Field(..., env="SNOWFLAKE_DATABASE")
    SNOWFLAKE_SCHEMA: str = Field("PUBLIC", env="SNOWFLAKE_SCHEMA")

    # Auth & Security Credentials
    JWT_SECRET: str = Field(..., env="JWT_SECRET")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    JWT_ACCESS_EXPIRE_MINUTES: int = Field(60, env="JWT_ACCESS_EXPIRE_MINUTES")
    JWT_REFRESH_EXPIRE_DAYS: int = Field(7, env="JWT_REFRESH_EXPIRE_DAYS")

    # Orchestration Settings
    N8N_BASE_URL: str = Field(..., env="N8N_WEBHOOK_BASE_URL")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
