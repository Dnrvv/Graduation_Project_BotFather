from aiogram import types, Dispatcher
from aiogram.utils.markdown import quote_html

from tgbot.keyboards.reply_kbs import main_menu_kb


async def bot_start(message: types.Message):
    await message.answer(f"Здравствуйте, {quote_html(message.from_user.full_name)}!", reply_markup=main_menu_kb)


def register_bot_start(dp: Dispatcher):
    dp.register_message_handler(bot_start, commands=["start"], state="*")

