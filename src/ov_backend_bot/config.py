from pathlib import Path

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env."""

    bot_token: SecretStr
    database_path: Path = PROJECT_ROOT / "data" / "bot.db"
    guide_path: Path = PROJECT_ROOT / "documents" / "python-development-guide.md"

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("database_path", "guide_path", mode="after")
    @classmethod
    def make_path_absolute(cls, value: Path) -> Path:
        if value.is_absolute():
            return value
        return PROJECT_ROOT / value
