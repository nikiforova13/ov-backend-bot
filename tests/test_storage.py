from pathlib import Path

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


@pytest.mark.asyncio
async def test_get_by_id_returns_none_for_unknown_user(tmp_path: Path) -> None:
    repository = UserRepository(tmp_path / "bot.db")
    await repository.initialize()

    assert await repository.get_by_id(999) is None
