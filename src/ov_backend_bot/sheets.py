import asyncio
import logging
from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

import gspread
from gspread.exceptions import WorksheetNotFound

from ov_backend_bot.config import Settings

logger = logging.getLogger(__name__)

HEADERS: tuple[str, ...] = (
    "Telegram ID",
    "Username",
    "Имя",
    "Фамилия",
    "Язык",
    "Premium",
    "Первый запуск",
    "Последний запуск",
    "Нажатий «Старт»",
    "Нажатий гайда",
)


def format_user_row(user: Mapping[str, object]) -> list[str]:
    return [
        _text(user.get("user_id")),
        _username(user.get("username")),
        _text(user.get("first_name")),
        _text(user.get("last_name")),
        _text(user.get("language_code")),
        _premium(user.get("is_premium")),
        _timestamp(user.get("first_seen_at")),
        _timestamp(user.get("last_seen_at")),
        _count(user.get("starts_count")),
        _count(user.get("guide_clicks")),
    ]


class GoogleUserSheet:
    """Publishes one row per Telegram user to a Google Sheet."""

    def __init__(self, worksheet: Any) -> None:
        self._worksheet = worksheet

    def sync_users(self, users: Sequence[Mapping[str, object]]) -> None:
        for user in users:
            self.upsert_user(user)

    def upsert_user(self, user: Mapping[str, object]) -> None:
        row = format_user_row(user)
        values = [list(existing) for existing in self._worksheet.get_all_values()]
        has_header = bool(values) and _is_header(values[0])
        data_rows = values[1:] if has_header else values

        user_id = row[0]
        replaced = False
        updated_rows: list[list[str]] = []
        for existing in data_rows:
            if not _has_cells(existing):
                continue
            if existing[0] == user_id:
                updated_rows.append(row)
                replaced = True
            else:
                updated_rows.append([str(cell) for cell in existing])
        if not replaced:
            updated_rows.append(row)

        table = [list(HEADERS), *updated_rows]
        self._worksheet.update(table, _table_range(len(table)))
        self._worksheet.format(_row_range(1), {"textFormat": {"bold": True}})
        if not has_header:
            self._worksheet.freeze(rows=1)


async def publish_user(
    user_sheet: GoogleUserSheet | None,
    user: Mapping[str, object] | None,
) -> None:
    if user_sheet is None or user is None:
        return
    try:
        await asyncio.to_thread(user_sheet.upsert_user, user)
    except Exception:
        logger.exception("Failed to write user %s to Google Sheet", user.get("user_id"))
    else:
        logger.info("Wrote user %s to Google Sheet", user.get("user_id"))


def service_account_info(settings: Settings) -> dict[str, str]:
    """Build the Google service-account payload from environment settings."""

    if (
        settings.google_project_id is None
        or settings.google_private_key_id is None
        or settings.google_private_key is None
        or settings.google_client_email is None
        or settings.google_client_id is None
        or settings.google_client_x509_cert_url is None
    ):
        raise ValueError("Google service account settings are incomplete")

    return {
        "type": "service_account",
        "project_id": settings.google_project_id,
        "private_key_id": settings.google_private_key_id.get_secret_value(),
        "private_key": settings.google_private_key.get_secret_value(),
        "client_email": settings.google_client_email,
        "client_id": settings.google_client_id,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": settings.google_client_x509_cert_url,
        "universe_domain": "googleapis.com",
    }


def open_user_sheet(
    credentials: Mapping[str, str],
    spreadsheet_id: str,
    worksheet_name: str | None = None,
) -> GoogleUserSheet:
    client = gspread.service_account_from_dict(credentials)
    spreadsheet = client.open_by_key(spreadsheet_id)
    if worksheet_name:
        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
        except WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(
                title=worksheet_name,
                rows=1000,
                cols=len(HEADERS),
            )
    else:
        worksheet = spreadsheet.sheet1
    logger.info("Connected to Google Sheet %s", spreadsheet_id)
    return GoogleUserSheet(worksheet)


def _is_header(row: list[object]) -> bool:
    return bool(row) and str(row[0]) == HEADERS[0]


def _has_cells(row: list[object]) -> bool:
    return any(str(cell).strip() for cell in row)


def _last_column() -> str:
    return chr(ord("A") + len(HEADERS) - 1)


def _row_range(row_number: int) -> str:
    return f"A{row_number}:{_last_column()}{row_number}"


def _table_range(row_count: int) -> str:
    return f"A1:{_last_column()}{row_count}"


def _text(value: object) -> str:
    if value is None:
        return ""
    return str(value)


def _count(value: object) -> str:
    if value is None or value == "":
        return "0"
    return str(value)


def _username(value: object) -> str:
    text = _text(value).strip()
    if text == "":
        return ""
    if text.startswith("@"):
        return text
    return f"@{text}"


def _premium(value: object) -> str:
    if value in (1, True, "1"):
        return "да"
    if value in (0, False, "0"):
        return "нет"
    return ""


def _timestamp(value: object) -> str:
    if value is None or value == "":
        return ""
    text = str(value)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return text
    return parsed.strftime("%d.%m.%Y %H:%M UTC")
