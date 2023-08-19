from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text="🛒 Сделать заказ")
        ],
        [
            KeyboardButton(text="📨 Оставить отзыв"),
            KeyboardButton(text="⚙️ Настройки")
        ],
        [
            KeyboardButton(text="🛍 Мои заказы")
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


cancel_order_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text="❌ Отменить заказ")
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
        resize_keyboard=True,
    )
    list_length = len(addresses)
    for counter in range(list_length):
        keyboard.row(KeyboardButton(text=f"{addresses[counter]}"),
                     KeyboardButton(text=f"{addresses[counter + 1]}"))
        counter += 1
        if counter - 1 == list_length:
            keyboard.add(KeyboardButton(text=f"{addresses[counter]}"))
            keyboard.add(KeyboardButton(text="⬅️ Назад"))
            break
    return keyboard
