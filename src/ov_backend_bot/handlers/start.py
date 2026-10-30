from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from ov_backend_bot.keyboards import guide_keyboard
from ov_backend_bot.storage import TelegramUser, UserRepository


def create_start_router(users: UserRepository) -> Router:
    router = Router(name="start")

    @router.message(CommandStart())
    async def handle_start(message: Message) -> None:
        if message.from_user is None:
            return

        await users.save_on_start(
            TelegramUser(
                user_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                language_code=message.from_user.language_code,
                is_premium=message.from_user.is_premium,
            )
        )

        await message.answer(
            "Привет! Я <b>O&amp;V Backend Bot</b>.\n\n"
            "Отправляю полезные материалы для backend-разработчиков. "
            "Нажми кнопку ниже, чтобы получить первый гайд.",
            reply_markup=guide_keyboard(),
        )

    return router
