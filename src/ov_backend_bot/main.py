import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from ov_backend_bot.config import Settings
from ov_backend_bot.handlers import create_guide_router, create_start_router
from ov_backend_bot.sheets import GoogleUserSheet, open_user_sheet, service_account_info
from ov_backend_bot.storage import UserRepository

logger = logging.getLogger(__name__)


async def main() -> None:
    settings = Settings()  # type: ignore[call-arg]
    if not settings.guide_path.is_file():
        raise FileNotFoundError(f"Guide file not found: {settings.guide_path}")

    users = UserRepository(settings.database_path)
    await users.initialize()
    user_sheet = _connect_user_sheet(settings)
    if user_sheet is not None:
        try:
            saved_users = await users.list_all()
            await asyncio.to_thread(user_sheet.sync_users, saved_users)
        except Exception:
            logger.exception("Failed to sync existing users to Google Sheet")
        else:
            logger.info("Synced %s users to Google Sheet", len(saved_users))

    dispatcher = Dispatcher()
    dispatcher.include_router(create_start_router(users, user_sheet))
    dispatcher.include_router(create_guide_router(settings.guide_path, users, user_sheet))

    bot = Bot(
        token=settings.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    try:
        await bot.set_my_commands(
            [
                BotCommand(command="start", description="Запустить бота"),
                BotCommand(command="python_guide", description="Получить гайд по Python"),
            ]
        )
        await dispatcher.start_polling(
            bot,
            allowed_updates=dispatcher.resolve_used_update_types(),
        )
    finally:
        await bot.session.close()


def _connect_user_sheet(settings: Settings) -> GoogleUserSheet | None:
    if not settings.uses_google_sheet():
        logger.info("Google Sheet is not configured. Users are stored in SQLite only")
        return None

    assert settings.google_spreadsheet_id is not None
    try:
        return open_user_sheet(
            service_account_info(settings),
            settings.google_spreadsheet_id,
            settings.google_worksheet_name,
        )
    except Exception:
        logger.exception("Google Sheet is unavailable. Users are stored in SQLite only")
        return None


def run() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    asyncio.run(main())


if __name__ == "__main__":
    run()
