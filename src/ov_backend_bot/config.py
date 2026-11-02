import os
from pathlib import Path

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _project_root() -> Path:
    configured = os.environ.get("APP_ROOT", "").strip()
    if configured:
        return Path(configured)
    return Path(__file__).resolve().parents[2]


PROJECT_ROOT = _project_root()


def normalize_spreadsheet_id(value: str) -> str:
    """Accept a raw spreadsheet id or a full Google Sheets URL."""

    text = value.strip()
    marker = "/spreadsheets/d/"
    if marker not in text:
        return text
    return text.split(marker, 1)[1].split("/", 1)[0].split("?", 1)[0]


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env."""

    bot_token: SecretStr
    database_path: Path = PROJECT_ROOT / "data" / "bot.db"
    guide_path: Path = PROJECT_ROOT / "documents" / "python-backend-roadmap.pdf"
    google_project_id: str | None = None
    google_private_key_id: SecretStr | None = None
    google_private_key: SecretStr | None = None
    google_client_email: str | None = None
    google_client_id: str | None = None
    google_client_x509_cert_url: str | None = None
    google_spreadsheet_id: str | None = None
    google_worksheet_name: str | None = None

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator(
        "google_project_id",
        "google_private_key_id",
        "google_client_email",
        "google_client_id",
        "google_client_x509_cert_url",
        "google_worksheet_name",
        mode="before",
    )
    @classmethod
    def blank_optional_setting(cls, value: object) -> object:
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return None
        return value

    @field_validator("google_private_key", mode="before")
    @classmethod
    def normalize_private_key(cls, value: object) -> object:
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return None
        if not isinstance(value, str):
            return value
        text = value
        if len(text) >= 2 and text[0] == text[-1] and text[0] in {'"', "'"}:
            text = text[1:-1]
        text = text.replace("\\n", "\n")
        if text.strip() == "":
            return None
        return text

    @field_validator("google_spreadsheet_id", mode="before")
    @classmethod
    def blank_spreadsheet_id(cls, value: object) -> object:
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return None
        if isinstance(value, str):
            return normalize_spreadsheet_id(value)
        return value

    @field_validator("database_path", "guide_path", mode="after")
    @classmethod
    def make_path_absolute(cls, value: Path) -> Path:
        if value.is_absolute():
            return value
        return PROJECT_ROOT / value

    def uses_google_sheet(self) -> bool:
        return all(
            (
                self.google_spreadsheet_id,
                self.google_project_id,
                self.google_private_key_id,
                self.google_private_key,
                self.google_client_email,
                self.google_client_id,
                self.google_client_x509_cert_url,
            )
        )
