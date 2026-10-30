from pathlib import Path

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, FSInputFile, Message

GUIDE_CAPTION = (
    "Готово! В файле — дорожная карта Python-разработчика, "
    "инструменты и практические рекомендации."
)


def create_guide_router(guide_path: Path) -> Router:
    router = Router(name="guides")

    async def send_guide(bot: Bot, chat_id: int) -> None:
        await bot.send_document(
            chat_id=chat_id,
            document=FSInputFile(guide_path, filename="python-development-guide.md"),
            caption=GUIDE_CAPTION,
        )

    @router.message(Command("python_guide"))
    async def handle_guide_command(message: Message, bot: Bot) -> None:
        await send_guide(bot, message.chat.id)

    @router.callback_query(F.data == "guide:python")
    async def handle_guide_button(callback: CallbackQuery, bot: Bot) -> None:
        await callback.answer()
        await send_guide(bot, callback.from_user.id)

    return router
