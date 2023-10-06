from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


check_subscription_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text="✅ Проверить подписку")
        ]
    ]
)


main_menu_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text="🛒 Сделать заказ")
        ],
        [
            KeyboardButton(text="✍️ Оставить отзыв"),
            KeyboardButton(text="🛍 Мои заказы")
        ],
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


reply_cancel_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text="❌ Отмена")
        ],
    ]
)


reply_approve_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text="✅ Да"),
            KeyboardButton(text="❌ Нет"),
        ],
    ]
)


get_contact_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text="📱 Мой номер", request_contact=True)
        ],
        [
            KeyboardButton(text="⬅️ Назад")
        ]
    ]
)

payment_type_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text="Наличные"),
        ],
        [
            KeyboardButton(text="Click"),
            KeyboardButton(text="Payme")
        ]
    ]
)


order_approve_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text="✅ Подтвердить"),
            KeyboardButton(text="❌ Отменить"),
        ],
    ]
)


def delivery_location_kb(has_addresses: bool = False):
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton(text="📍 Поделиться геопозицией", request_location=True),
            ],
        ]
    )
    if has_addresses:
        keyboard.row(KeyboardButton(text="🗺 Мои адреса"), KeyboardButton(text="❌ Отмена"))
    else:
        keyboard.add(KeyboardButton(text="❌ Отмена"))
    return keyboard


def saved_locations_kb(addresses: list):
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True, row_width=2
    )
    for address in addresses:
        keyboard.insert(KeyboardButton(address))
    keyboard.add(KeyboardButton(text="⬅️ Назад"))
    return keyboard
