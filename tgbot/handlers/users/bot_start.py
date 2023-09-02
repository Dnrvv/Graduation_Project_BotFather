import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageToDeleteNotFound
from aiogram.utils.markdown import quote_html

from tgbot.keyboards.reply_kbs import main_menu_kb
from tgbot.middlewares.throttling import rate_limit
from tgbot.misc.dependences import SUPPORT_USERNAME


async def bot_start(message: types.Message, state: FSMContext):
    state_name = await state.get_state()
    if state_name:
        if "Order" in state_name:
            async with state.proxy() as data:
                top_msg_id = data.get("top_msg_id")
                menu_msg_id = data.get("menu_msg_id")
                ph_msg_id = data.get("ph_msg_id")

            try:
                if top_msg_id:
                    await message.bot.delete_message(chat_id=message.from_user.id, message_id=top_msg_id)
                if ph_msg_id:
                    await message.bot.delete_message(chat_id=message.from_user.id, message_id=ph_msg_id)
                if menu_msg_id:
                    await message.bot.delete_message(chat_id=message.from_user.id, message_id=menu_msg_id)
            except MessageToDeleteNotFound as error:
                logging.error(error)
                pass

            await message.answer("😔 Заказ отменён", reply_markup=main_menu_kb)
    else:
        await message.answer(f"Здравствуйте, {quote_html(message.from_user.full_name)}!", reply_markup=main_menu_kb)

    await state.reset_data()
    await state.finish()


@rate_limit(1)
async def get_help(message: types.Message):
    await message.answer("🛠 Если что-то пошло не так, нажмите <b>/start</b>, чтобы перезапустить бота. "
                         f"Пожалуйста, сообщите об ошибке разработчику: <b>{SUPPORT_USERNAME}</b>")


def register_bot_start(dp: Dispatcher):
    dp.register_message_handler(bot_start, commands="start", state="*")
    dp.register_message_handler(get_help, commands=["help"], state="*")
