from aiogram import types, Dispatcher

from tgbot.keyboards.reply_kbs import main_menu_kb


async def bot_start(message: types.Message):
    await message.answer("Отлично, вы зарегистрированы в бд!", reply_markup=main_menu_kb)


def register_bot_start(dp: Dispatcher):
    dp.register_message_handler(bot_start, commands=["start"], state="*")

