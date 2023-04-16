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
