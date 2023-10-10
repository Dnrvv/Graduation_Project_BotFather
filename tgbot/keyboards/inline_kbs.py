from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData


notify_users_approve_callback = CallbackData("action", "approve")
notify_users_approves = ["send", "cancel"]
notify_users_approve_kb = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✉️ Отправить", callback_data=notify_users_approve_callback.new(approve="send")),
            InlineKeyboardButton(text="❌ Отмена", callback_data=notify_users_approve_callback.new(approve="cancel"))
        ]
    ]
)

choose_payment_method_cd = CallbackData("payment", "method")
payment_methods_list = ["uzcard", "visa_usd", "cancel"]
choose_payment_method_kb = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Uzcard", callback_data=choose_payment_method_cd.new(method="uzcard")),
            InlineKeyboardButton(text="Visa USD", callback_data=choose_payment_method_cd.new(method="visa_usd"))
        ],
        [
            InlineKeyboardButton(text="❌Отмена", callback_data=choose_payment_method_cd.new(method="cancel"))
        ]
    ]
)
