from aiogram import types, Dispatcher
from tgbot.middlewares.throttling import rate_limit
from tgbot.misc.dependences import SUPPORT_USERNAME


@rate_limit(1)
async def get_help(message: types.Message):
    await message.answer("🛠 Если что-то пошло не так, нажмите <b>/start</b>, чтобы перезапустить бота. "
                         f"Пожалуйста, сообщите об ошибке разработчику: <b>{SUPPORT_USERNAME}</b>")


def register_user_commands(dp: Dispatcher):
    dp.register_message_handler(get_help, commands=["help"], state="*")
