import logging
import re

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.utils.exceptions import MessageToDeleteNotFound
from aiogram.utils.markdown import quote_html
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.infrastructure.database.db_functions import user_functions
from tgbot.infrastructure.database.db_models.user_models import User
from tgbot.keyboards.reply_kbs import main_menu_kb
from tgbot.middlewares.throttling import rate_limit
from tgbot.misc.dependences import SUPPORT_USERNAME, BOT_USERNAME, CHANNEL_USERNAME
from tgbot.services.broadcast_functions import send_text
from tgbot.services.service_functions import is_subscribed, format_number_with_spaces


@rate_limit(1)
async def deeplink_bot_start(message: types.Message, session: AsyncSession):
    referer_id = message.get_args()
    referer_obj = await user_functions.get_user(session, telegram_id=int(referer_id))
    if not referer_obj:
        await message.answer("😔 Ссылка недействительна.")
        return

    referral_obj = await user_functions.get_user(session, telegram_id=int(message.from_user.id))
    if referral_obj:
        await message.answer("😄 Вы уже активировали эту ссылку.")
        return

    await user_functions.add_user(session, telegram_id=message.from_user.id, full_name=message.from_user.full_name,
                                  role="User")
    await user_functions.update_user(session, User.telegram_id == referer_obj.telegram_id, balance=referer_obj.balance+15000)
    await user_functions.update_user(session, User.telegram_id == message.from_user.id, balance=100000)
    await session.commit()

    text = "🎉 По вашей ссылке зарегистрировался пользователь. На Ваш баланс начислен бонус в размере 15 000 сум."
    await send_text(bot=message.bot, user_id=int(referer_id), text=text)
    await message.answer(f"Здравствуйте, {quote_html(message.from_user.full_name)}!\n"
                         f"На Ваш баланс начислен бонус в размере 100 000 сум.", reply_markup=main_menu_kb)


@rate_limit(1)
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
        await message.answer(f"Здравствуйте, {message.from_user.full_name}!", reply_markup=main_menu_kb)
    await state.reset_data()
    await state.finish()


@rate_limit(1)
async def subscription_check(message: types.Message, session: AsyncSession):
    if not await is_subscribed(user_id=message.from_user.id, channel=CHANNEL_USERNAME):
        text = (f"😋 Для доступа к боту Вам необходимо подписаться на канал: <b>{CHANNEL_USERNAME}</b>."
                f"\n\n<i>После подписки нажмите на кнопку ниже:</i>")
        await message.answer(text=text)
        return

    user_obj = await user_functions.get_user(session, telegram_id=int(message.from_user.id))
    if user_obj:
        await message.answer("😄 Вы уже получили доступ.")
        return

    await user_functions.add_user(session, telegram_id=message.from_user.id, full_name=message.from_user.full_name,
                                  role="User")
    await user_functions.update_user(session, User.telegram_id == message.from_user.id, balance=100000)
    await message.answer(f"Здравствуйте, {quote_html(message.from_user.full_name)}!\n"
                         f"На Ваш баланс начислен бонус в размере 100 000 сум.", reply_markup=main_menu_kb)
    await session.commit()


@rate_limit(1)
async def get_user_balance(message: types.Message, session: AsyncSession):
    user_obj = await user_functions.get_user(session, telegram_id=message.from_user.id)
    await message.answer(f"💳 Ваш баланс: {format_number_with_spaces(user_obj.balance)} сум.")


@rate_limit(1)
async def get_user_referer_link(message: types.Message):
    link = f"https://t.me/{BOT_USERNAME}/?start={message.from_user.id}"
    await message.answer(f"🔖 Ваша реферальная ссылка: <code>{link}</code>")


@rate_limit(1)
async def get_help(message: types.Message):
    await message.answer("🛠 Если что-то пошло не так, нажмите <b>/start</b>, чтобы перезапустить бота. "
                         f"Пожалуйста, сообщите об ошибке разработчику: <b>{SUPPORT_USERNAME}</b>")


def register_bot_start(dp: Dispatcher):
    dp.register_message_handler(deeplink_bot_start, CommandStart(deep_link=re.compile(r"^[a-zA-Z0-9]{1,10}$")),
                                state="*")
    dp.register_message_handler(bot_start, commands="start", state="*")
    dp.register_message_handler(subscription_check, text="✅ Проверить подписку", state="*")
    dp.register_message_handler(get_user_balance, commands="my_balance", state="*")
    dp.register_message_handler(get_user_referer_link, commands="my_referer_link", state="*")
    dp.register_message_handler(get_help, commands="help", state="*")
