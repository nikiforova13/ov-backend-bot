from ov_backend_bot.config import normalize_spreadsheet_id
from ov_backend_bot.sheets import HEADERS, GoogleUserSheet


class MemoryWorksheet:
    def __init__(self) -> None:
        self.rows: list[list[str]] = []
        self.frozen_rows = 0

    def get_all_values(self) -> list[list[str]]:
        return [list(row) for row in self.rows]

    def update(self, values: list[list[str]], range_name: str) -> None:
        row_number = int("".join(char for char in range_name.split(":")[0] if char.isdigit()))
        start = row_number - 1
        for offset, row in enumerate(values):
            index = start + offset
            while len(self.rows) <= index:
                self.rows.append([])
            self.rows[index] = [str(value) for value in row]

    def format(self, range_name: str, cell_format: dict[str, object]) -> None:
        del range_name, cell_format

    def freeze(self, rows: int | None = None, cols: int | None = None) -> None:
        del cols
        self.frozen_rows = rows or 0


def test_normalize_spreadsheet_id_from_url() -> None:
    url = "https://docs.google.com/spreadsheets/d/abc123_XYZ/edit?gid=0#gid=0"
    assert normalize_spreadsheet_id(url) == "abc123_XYZ"
    assert normalize_spreadsheet_id("  abc123_XYZ  ") == "abc123_XYZ"


def test_upsert_user_creates_header_and_updates_same_row() -> None:
    worksheet = MemoryWorksheet()
    sheet = GoogleUserSheet(worksheet)
    user = {
        "user_id": 42,
        "username": "olya",
        "first_name": "Ольга",
        "last_name": None,
        "language_code": "ru",
        "is_premium": 0,
        "first_seen_at": "2026-10-30T13:09:24.422Z",
        "last_seen_at": "2026-10-30T13:09:24.422Z",
        "starts_count": 1,
    }

    sheet.upsert_user(user)
    sheet.upsert_user(
        {
            **user,
            "username": "olyaiev",
            "is_premium": 1,
            "last_seen_at": "2026-10-30T13:15:00.000Z",
            "starts_count": 2,
        }
    )

    assert worksheet.rows[0] == list(HEADERS)
    assert len(worksheet.rows) == 2
    assert worksheet.rows[1] == [
        "42",
        "@olyaiev",
        "Ольга",
        "",
        "ru",
        "да",
        "30.10.2026 13:09 UTC",
        "30.10.2026 13:15 UTC",
        "2",
        "0",
    ]
    assert worksheet.frozen_rows == 1


def test_upsert_user_adds_header_above_existing_row() -> None:
    worksheet = MemoryWorksheet()
    worksheet.rows = [["42", "@olya", "Ольга", "", "ru", "нет", "", "", "1"]]
    sheet = GoogleUserSheet(worksheet)

    sheet.upsert_user(
        {
            "user_id": 42,
            "username": "olyaiev",
            "first_name": "Ольга",
            "last_name": None,
            "language_code": "ru",
            "is_premium": 1,
            "first_seen_at": "2026-10-30T13:09:24.422Z",
            "last_seen_at": "2026-10-30T13:15:00.000Z",
            "starts_count": 2,
        }
    )

    assert worksheet.rows[0] == list(HEADERS)
    assert worksheet.rows[1][1] == "@olyaiev"
    assert worksheet.rows[1][-1] == "0"
    assert len(worksheet.rows) == 2


def test_upsert_user_replaces_previous_header() -> None:
    worksheet = MemoryWorksheet()
    worksheet.rows = [
        ["Telegram ID", "Username", "Запусков"],
        ["42", "@olya", "1"],
    ]
    sheet = GoogleUserSheet(worksheet)

    sheet.upsert_user(
        {
            "user_id": 42,
            "username": "olyaiev",
            "first_name": "Ольга",
            "last_name": None,
            "language_code": "ru",
            "is_premium": 1,
            "first_seen_at": "2026-10-30T13:09:24.422Z",
            "last_seen_at": "2026-10-30T13:15:00.000Z",
            "starts_count": 2,
            "guide_clicks": 3,
        }
    )

    assert worksheet.rows[0] == list(HEADERS)
    assert len(worksheet.rows) == 2
    assert worksheet.rows[1][-2:] == ["2", "3"]
