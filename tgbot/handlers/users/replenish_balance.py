import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageToDeleteNotFound
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.config import load_config
from tgbot.infrastructure.database.db_functions import user_functions, currency_functions
from tgbot.infrastructure.database.db_models.user_models import User
from tgbot.keyboards.inline_kbs import choose_payment_method_cd, payment_methods_list
from tgbot.keyboards.reply_kbs import main_menu_kb, reply_cancel_kb
from tgbot.middlewares.throttling import rate_limit
from tgbot.misc.states import ReplenishBalance
from tgbot.services.service_functions import format_number_with_spaces


async def get_payment_method(call: types.CallbackQuery, callback_data: dict, state: FSMContext, session: AsyncSession):
    await call.answer()
    await call.message.delete_reply_markup()
    method = callback_data.get("method")
    currency = ""
    if method == "cancel":
        await call.message.edit_text("❌ Операция отменена.")
        await state.reset_data()
        await state.reset_state()

    elif method == "uzcard":
        currency = "UZS"

    elif method == "visa_usd":
        currency = "USD"

    await state.update_data(currency=currency)
    try:
        currency_obj = await currency_functions.get_currency(session, currency_code=currency)
        text = (f"Введите сумму пополнения ({currency}):\n\n"
                f"<b>1 {currency} = {int(currency_obj.course_to_uzs)} сум</b>")
    except AttributeError as err:
        logging.error(err)
        text = "Введите сумму пополнения:"
    await call.message.answer(text=text, reply_markup=reply_cancel_kb)
    await ReplenishBalance.GetReplenishAmount.set()


@rate_limit(1)
async def get_replenish_amount(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        currency = data.get("currency")

    if not message.text.isdigit():
        await message.answer("❗️ Пожалуйста, отправьте числовое значение. Без пробелов и прочих символов.")
        return

    description = "😋 Пополните баланс и закажите вкусняшек!"

    if currency == "UZS":
        provider_token = load_config().tg_bot.uzcard_provider_token
    else:
        provider_token = load_config().tg_bot.visa_provider_token
    invoice_msg = await message.bot.send_invoice(chat_id=message.from_user.id, title="Пополнение баланса",
                                                 description=description, provider_token=provider_token,
                                                 currency=currency,
                                                 prices=[types.LabeledPrice(label="Пополнение баланса:",
                                                                            amount=int(message.text) * 100)],
                                                 payload="123456")

    await state.update_data(amount=message.text, invoice_msg_id=invoice_msg.message_id)
    await ReplenishBalance.Checkout.set()


async def replenish_pre_checkout(pre_checkout_query: types.PreCheckoutQuery, state: FSMContext, session: AsyncSession):
    async with state.proxy() as data:
        currency = data.get("currency")
        amount = int(data.get("amount"))
        invoice_msg_id = data.get("invoice_msg_id")

    if currency == "USD":
        currency_obj = await currency_functions.get_currency(session, currency_code=currency)
        amount = amount * int(currency_obj.course_to_uzs)

    await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query_id=pre_checkout_query.id,
                                                           ok=True)
    user_obj = await user_functions.get_user(session, telegram_id=pre_checkout_query.from_user.id)

    await user_functions.update_user(session, User.telegram_id == pre_checkout_query.from_user.id,
                                     balance=user_obj.balance + amount)
    await session.commit()
    await pre_checkout_query.bot.delete_message(chat_id=pre_checkout_query.from_user.id, message_id=invoice_msg_id)
    await pre_checkout_query.bot.send_message(chat_id=pre_checkout_query.from_user.id,
                                              text=f"✅ На Ваш баланс начислено {format_number_with_spaces(amount)} "
                                                   f"сум.", reply_markup=main_menu_kb)
    await state.reset_data()
    await state.reset_state()


@rate_limit(1)
async def cancel_replenish_operation(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        invoice_msg_id = data.get("invoice_msg_id")

    try:
        if invoice_msg_id:
            await message.bot.delete_message(chat_id=message.from_user.id, message_id=invoice_msg_id)
    except MessageToDeleteNotFound as error:
        logging.error(error)
        pass

    await message.answer("❌ Операция отменена.", reply_markup=main_menu_kb)
    await state.reset_data()
    await state.reset_state()


def register_replenish_balance(dp: Dispatcher):
    dp.register_callback_query_handler(get_payment_method, choose_payment_method_cd.filter(method=payment_methods_list),
                                       state=ReplenishBalance.GetPaymentMethod)
    dp.register_message_handler(cancel_replenish_operation, text="❌ Отмена",
                                state=[ReplenishBalance.GetReplenishAmount, ReplenishBalance.Checkout])
    dp.register_message_handler(get_replenish_amount, content_types=types.ContentType.TEXT,
                                state=ReplenishBalance.GetReplenishAmount)
    dp.register_pre_checkout_query_handler(replenish_pre_checkout, state=ReplenishBalance.Checkout)

