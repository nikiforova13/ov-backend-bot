from dataclasses import dataclass
from pathlib import Path

import aiosqlite


@dataclass(frozen=True, slots=True)
class TelegramUser:
    user_id: int
    username: str | None
    first_name: str
    last_name: str | None
    language_code: str | None
    is_premium: bool | None


class UserRepository:
    """Stores Telegram users who started the bot."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    async def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self.database_path) as connection:
            await connection.execute(
                """
                CREATE TABLE IF NOT EXISTS telegram_users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT NOT NULL,
                    last_name TEXT,
                    language_code TEXT,
                    is_premium INTEGER,
                    first_seen_at TEXT NOT NULL
                        DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
                    last_seen_at TEXT NOT NULL
                        DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
                    starts_count INTEGER NOT NULL DEFAULT 1
                )
                """
            )
            await connection.commit()

    async def save_on_start(self, user: TelegramUser) -> None:
        async with aiosqlite.connect(self.database_path) as connection:
            await connection.execute(
                """
                INSERT INTO telegram_users (
                    user_id,
                    username,
                    first_name,
                    last_name,
                    language_code,
                    is_premium
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username = excluded.username,
                    first_name = excluded.first_name,
                    last_name = excluded.last_name,
                    language_code = excluded.language_code,
                    is_premium = excluded.is_premium,
                    last_seen_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now'),
                    starts_count = telegram_users.starts_count + 1
                """,
                (
                    user.user_id,
                    user.username,
                    user.first_name,
                    user.last_name,
                    user.language_code,
                    user.is_premium,
                ),
            )
            await connection.commit()

    async def get_by_id(self, user_id: int) -> dict[str, object] | None:
        async with aiosqlite.connect(self.database_path) as connection:
            connection.row_factory = aiosqlite.Row
            cursor = await connection.execute(
                "SELECT * FROM telegram_users WHERE user_id = ?",
                (user_id,),
            )
            row = await cursor.fetchone()
            return dict(row) if row else None
