import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from ov_backend_bot.config import Settings
from ov_backend_bot.handlers import create_guide_router, create_start_router
from ov_backend_bot.storage import UserRepository


async def main() -> None:
    settings = Settings()  # type: ignore[call-arg]
    if not settings.guide_path.is_file():
        raise FileNotFoundError(f"Guide file not found: {settings.guide_path}")

    users = UserRepository(settings.database_path)
    await users.initialize()

    dispatcher = Dispatcher()
    dispatcher.include_router(create_start_router(users))
    dispatcher.include_router(create_guide_router(settings.guide_path))

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


def run() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    asyncio.run(main())


if __name__ == "__main__":
    run()
