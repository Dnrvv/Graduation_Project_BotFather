from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text="Кнопка 1")
        ],
    ]
)
