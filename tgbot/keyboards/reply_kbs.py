from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text="Сделать заказ")
        ],
        [
            KeyboardButton(text="Оставить отзыв"),
            KeyboardButton(text="Настройки")
        ],
        [
            KeyboardButton(text="Мои заказы")
        ]
    ]
)

order_type_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text="🛵 Доставка"),
            KeyboardButton(text="🚶 Самовывоз"),
        ],
        [
            KeyboardButton(text="❌ Отмена")
        ],
    ]
)
