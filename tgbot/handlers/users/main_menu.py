from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.infrastructure.database.db_functions import order_functions, user_functions, product_functions
from tgbot.infrastructure.database.db_functions.feedback_functions import add_feedback
from tgbot.keyboards.inline_kbs import choose_payment_method_kb
from tgbot.keyboards.pagination_kbs import user_orders_kb, orders_pagination_call_cd
from tgbot.keyboards.reply_kbs import main_menu_kb, reply_cancel_kb, location_methods_kb
from tgbot.middlewares.throttling import rate_limit
from tgbot.misc.dependences import MAX_FEEDBACK_LENGTH
from tgbot.misc.states import Order, Feedback, ReplenishBalance
from tgbot.services.text_formatting_functions import create_order_history_text


@rate_limit(1)
async def make_order(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.reset_data()
    user_obj = await user_functions.get_user(session, telegram_id=message.from_user.id)
    if user_obj.balance < await product_functions.get_the_cheapest_product_price(session):
        await message.answer("😔 На Вашем балансе недостаточно средств.")
        return

    flag = await user_functions.check_user_addresses(session, cust_telegram_id=message.from_user.id)
    if flag:
        await message.answer("📍 Отправьте геопозицию или выберите адрес из сохранённых:",
                             reply_markup=location_methods_kb(has_addresses=flag))
    else:
        await message.answer("📍 Отправьте геопозицию:", reply_markup=location_methods_kb(has_addresses=flag))
    await Order.GetLocation.set()


@rate_limit(1)
async def replenish_balance(message: types.Message):
    text = ("Выберите метод оплаты:\n\n"
            "ℹ️ <i>Примечание: при выборе сторонних валют (например <b>USD</b>), после оплаты произойдёт конвертация "
            "по текущему курсу ЦБ РУз.</i>")
    await message.answer(text=text, reply_markup=choose_payment_method_kb)
    await ReplenishBalance.GetPaymentMethod.set()


@rate_limit(1)
async def user_orders(message: types.Message, session: AsyncSession):
    orders_count = await order_functions.get_user_orders_count(session, cust_telegram_id=message.from_user.id)
    if orders_count == 0:
        await message.answer("🤔 Вы ещё ничего не заказывали.")
        return
    order_obj = await order_functions.get_user_order_pagination(session, cust_telegram_id=message.from_user.id,
                                                                counter=1)
    text = await create_order_history_text(order_obj, session)
    await message.answer(text=text, reply_markup=user_orders_kb(orders_count=orders_count))


async def show_chosen_page(call: types.CallbackQuery, callback_data: dict, session: AsyncSession):
    current_page = callback_data.get("page")
    if current_page == "cancel":
        await call.answer()
        await call.message.edit_text("😋 Ням-ням!")
        return
    elif current_page == "begin_empty":
        await call.answer("Вы в самом начале списка!", show_alert=False)
        return
    elif current_page == "end_empty":
        await call.answer("Вы достигли конца списка!", show_alert=False)
        return
    await call.answer()
    orders_count = await order_functions.get_user_orders_count(session, cust_telegram_id=call.from_user.id)
    order_obj = await order_functions.get_user_order_pagination(session, cust_telegram_id=call.from_user.id,
                                                                counter=int(current_page))

    text = await create_order_history_text(order_obj, session)
    keyboard = user_orders_kb(orders_count=orders_count, page=int(current_page))
    await call.message.edit_text(text=text, reply_markup=keyboard)


@rate_limit(1)
async def feedback(message: types.Message, state: FSMContext):
    await message.answer("📨 Мы будем рады, если Вы оставите отзыв:", reply_markup=reply_cancel_kb)
    await state.reset_data()
    await Feedback.GetFeedbackText.set()


@rate_limit(1)
async def save_feedback(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == "❌ Отмена":
        await message.answer("Действие отменено.", reply_markup=main_menu_kb)
    elif len(message.text) > MAX_FEEDBACK_LENGTH:
        await message.answer(f"❗️ Длина отзыва должна составлять не более {MAX_FEEDBACK_LENGTH} символов. "
                             f"Попробуйте снова:")
        return
    else:
        await add_feedback(session, cust_telegram_id=message.from_user.id, feedback_text=message.text)
        await session.commit()
        await message.reply("❣️ Спасибо! Ваш отзыв отправлен администрации.", reply_markup=main_menu_kb)
    await state.reset_data()
    await state.finish()


def register_main_menu(dp: Dispatcher):
    dp.register_message_handler(make_order, text=["🛒 Сделать заказ", "/order"], state="*")

    dp.register_message_handler(replenish_balance, text="💳 Пополнить баланс", state="*")

    dp.register_message_handler(user_orders, text="🛍 Мои заказы", state="*")
    dp.register_callback_query_handler(show_chosen_page, orders_pagination_call_cd.filter(), state="*")

    dp.register_message_handler(feedback, text=["✍️ Оставить отзыв", "/feedback"], state="*")
    dp.register_message_handler(save_feedback, content_types=types.ContentType.TEXT,
                                state=Feedback.GetFeedbackText)
