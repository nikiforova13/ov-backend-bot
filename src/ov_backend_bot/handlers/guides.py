from pathlib import Path

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, FSInputFile, Message

from ov_backend_bot.sheets import GoogleUserSheet, publish_user
from ov_backend_bot.storage import UserRepository

GUIDE_CAPTION = (
    "Гайд по backend на Python.\n\n"
    "Внутри порядок тем, план на 12 недель и что положить в репозиторий."
)


def create_guide_router(
    guide_path: Path,
    users: UserRepository,
    user_sheet: GoogleUserSheet | None = None,
) -> Router:
    router = Router(name="guides")

    async def send_guide(bot: Bot, chat_id: int) -> None:
        await bot.send_document(
            chat_id=chat_id,
            document=FSInputFile(guide_path, filename="python-backend-roadmap.pdf"),
            caption=GUIDE_CAPTION,
        )

    @router.message(Command("python_guide"))
    async def handle_guide_command(message: Message, bot: Bot) -> None:
        await send_guide(bot, message.chat.id)

    @router.callback_query(F.data == "guide:python")
    async def handle_guide_button(callback: CallbackQuery, bot: Bot) -> None:
        await callback.answer()
        saved_user = await users.record_guide_click(callback.from_user.id)
        await send_guide(bot, callback.from_user.id)
        await publish_user(user_sheet, saved_user)

    return router
