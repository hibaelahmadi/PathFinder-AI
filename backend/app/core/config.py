from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr


BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int = 5432
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    JWT_SECRET_KEY: SecretStr = Field(min_length=32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, ge=1, le=1440)
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    QUESTIONNAIRE_ENRICH_PROFILE: bool = False

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
    )
