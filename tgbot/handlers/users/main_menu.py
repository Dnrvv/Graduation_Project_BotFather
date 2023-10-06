from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.infrastructure.database.db_functions import order_functions
from tgbot.infrastructure.database.db_functions.user_functions import add_user_feedback
from tgbot.keyboards.pagination_kbs import user_orders_kb, orders_pagination_call_cd
from tgbot.keyboards.reply_kbs import order_type_kb, main_menu_kb, reply_cancel_kb
from tgbot.middlewares.throttling import rate_limit
from tgbot.misc.states import Order, Feedback
from tgbot.services.text_formatting_functions import create_order_text


@rate_limit(1)
async def make_order(message: types.Message, state: FSMContext):
    await state.reset_data()
    await message.answer("Выберите тип заказа:", reply_markup=order_type_kb)
    await Order.GetOrderType.set()


@rate_limit(1)
async def feedback(message: types.Message, state: FSMContext):
    await message.answer("📨 Мы будем рады, если Вы оставите отзыв:", reply_markup=reply_cancel_kb)
    await state.reset_data()
    await Feedback.GetFeedbackText.set()


@rate_limit(1)
async def user_orders(message: types.Message, session: AsyncSession):
    orders_count = await order_functions.get_user_orders_count(session, cust_telegram_id=message.from_user.id)
    if orders_count == 0:
        await message.answer("🤔 Вы ещё ничего не заказывали.")
        return
    order_obj = await order_functions.get_user_order_pagination(session, cust_telegram_id=message.from_user.id,
                                                                counter=1)
    text = await create_order_text(order_obj, session)
    await message.answer(text=text, reply_markup=user_orders_kb(orders_count=orders_count))


async def show_chosen_page(call: types.CallbackQuery, callback_data: dict, session: AsyncSession):
    current_page = callback_data.get("page")
    if current_page == "cancel":
        await call.answer()
        await call.message.edit_text("😋 Ням-ням.")
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

    text = await create_order_text(order_obj, session)
    keyboard = user_orders_kb(orders_count=orders_count, page=int(current_page))
    await call.message.edit_text(text=text, reply_markup=keyboard)


@rate_limit(1)
async def save_feedback(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == "❌ Отмена":
        await message.answer("Действие отменено.", reply_markup=main_menu_kb)
    else:
        await add_user_feedback(session, cust_telegram_id=message.from_user.id, feedback_text=message.text)
        await session.commit()
        await message.reply("❣️ Спасибо! Ваш отзыв отправлен администрации.", reply_markup=main_menu_kb)
    await state.reset_data()
    await state.finish()


def register_main_menu(dp: Dispatcher):
    dp.register_message_handler(make_order, text=["🛒 Сделать заказ", "/order"], state="*")

    # FEEDBACK
    dp.register_message_handler(feedback, text=["✍️ Оставить отзыв", "/feedback"], state="*")
    dp.register_message_handler(save_feedback, content_types=types.ContentType.TEXT,
                                state=Feedback.GetFeedbackText)

    # USER ORDERS
    dp.register_message_handler(user_orders, text="🛍 Мои заказы", state="*")
    dp.register_callback_query_handler(show_chosen_page, orders_pagination_call_cd.filter(), state="*")
