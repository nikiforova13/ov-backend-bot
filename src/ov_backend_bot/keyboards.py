from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def guide_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🐍 Получить гайд по Python-разработке",
                    callback_data="guide:python",
                )
            ]
        ]
    )
