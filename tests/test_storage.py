from pathlib import Path

import aiosqlite
import pytest

from ov_backend_bot.storage import TelegramUser, UserRepository


@pytest.mark.asyncio
async def test_save_on_start_creates_and_updates_user(tmp_path: Path) -> None:
    repository = UserRepository(tmp_path / "bot.db")
    await repository.initialize()

    await repository.save_on_start(
        TelegramUser(
            user_id=42,
            username="first_username",
            first_name="Ольга",
            last_name=None,
            language_code="ru",
            is_premium=False,
        )
    )
    await repository.save_on_start(
        TelegramUser(
            user_id=42,
            username="updated_username",
            first_name="Ольга",
            last_name="Никифорова",
            language_code="ru",
            is_premium=True,
        )
    )

    saved_user = await repository.get_by_id(42)

    assert saved_user is not None
    assert saved_user["username"] == "updated_username"
    assert saved_user["last_name"] == "Никифорова"
    assert saved_user["is_premium"] == 1
    assert saved_user["starts_count"] == 2
    assert saved_user["guide_clicks"] == 0


@pytest.mark.asyncio
async def test_list_all_returns_saved_users(tmp_path: Path) -> None:
    repository = UserRepository(tmp_path / "bot.db")
    await repository.initialize()
    await repository.save_on_start(
        TelegramUser(
            user_id=7,
            username=None,
            first_name="Ольга",
            last_name=None,
            language_code="ru",
            is_premium=None,
        )
    )

    saved_users = await repository.list_all()

    assert [user["user_id"] for user in saved_users] == [7]


@pytest.mark.asyncio
async def test_get_by_id_returns_none_for_unknown_user(tmp_path: Path) -> None:
    repository = UserRepository(tmp_path / "bot.db")
    await repository.initialize()

    assert await repository.get_by_id(999) is None


@pytest.mark.asyncio
async def test_record_guide_click_increments_without_changing_starts(tmp_path: Path) -> None:
    repository = UserRepository(tmp_path / "bot.db")
    await repository.initialize()
    await repository.save_on_start(
        TelegramUser(
            user_id=42,
            username="olyaiev",
            first_name="Ольга",
            last_name=None,
            language_code="ru",
            is_premium=True,
        )
    )

    await repository.record_guide_click(42)
    saved_user = await repository.record_guide_click(42)

    assert saved_user is not None
    assert saved_user["starts_count"] == 1
    assert saved_user["guide_clicks"] == 2
    assert await repository.record_guide_click(999) is None


@pytest.mark.asyncio
async def test_initialize_adds_guide_clicks_to_existing_database(tmp_path: Path) -> None:
    database_path = tmp_path / "bot.db"
    async with aiosqlite.connect(database_path) as connection:
        await connection.execute(
            """
            CREATE TABLE telegram_users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT NOT NULL,
                last_name TEXT,
                language_code TEXT,
                is_premium INTEGER,
                first_seen_at TEXT NOT NULL,
                last_seen_at TEXT NOT NULL,
                starts_count INTEGER NOT NULL DEFAULT 1
            )
            """
        )
        await connection.execute(
            """
            INSERT INTO telegram_users (
                user_id, username, first_name, last_name, language_code,
                is_premium, first_seen_at, last_seen_at, starts_count
            ) VALUES (
                1, 'olyaiev', 'Olya', NULL, 'ru', 1,
                '2026-10-30T13:09:24.422Z', '2026-10-30T13:09:24.422Z', 2
            )
            """
        )
        await connection.commit()

    repository = UserRepository(database_path)
    await repository.initialize()
    saved_user = await repository.record_guide_click(1)

    assert saved_user is not None
    assert saved_user["starts_count"] == 2
    assert saved_user["guide_clicks"] == 1
