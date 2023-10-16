from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.infrastructure.database.db_functions import user_functions, order_functions, feedback_functions
from tgbot.keyboards.pagination_kbs import feedbacks_kb, feedbacks_pagination_call_cd
from tgbot.keyboards.reply_kbs import main_menu_kb
from tgbot.middlewares.throttling import rate_limit
from tgbot.misc.states import AdminActions


@rate_limit(1)
async def get_bot_statistics(message: types.Message, session: AsyncSession):
    users_count = await user_functions.get_users_count(session)
    orders_count = await order_functions.get_orders_count(session)
    await message.answer(f"📑 Статистика:\n"
                         f"• Зарегистрировано пользователей: <b>{users_count}</b> чел.\n"
                         f"• Сделано заказов: <b>{orders_count}</b> шт.")


@rate_limit(1)
async def show_feedbacks(message: types.Message, state: FSMContext, session: AsyncSession):
    feedback_obj = await feedback_functions.get_feedback(session, feedback_num=1)
    if not feedback_obj:
        await message.answer("🤔 Пользователи ещё не писали отзывов.")
        return
    text = f"📨 Отзыв №1: \n{feedback_obj.feedback_text}"
    feedbacks_count = await feedback_functions.get_feedbacks_count(session)
    top_msg = await message.answer("Отзывы пользователей:", reply_markup=ReplyKeyboardRemove())
    await message.answer(text=text, reply_markup=feedbacks_kb(feedbacks_count=feedbacks_count))
    await AdminActions.FeedbacksChecking.set()
    await state.update_data(previous_page=0, feedback_num=1, feedbacks_count=feedbacks_count,
                            top_msg_id=top_msg.message_id)


async def show_chosen_page(call: types.CallbackQuery, callback_data: dict, state: FSMContext, session: AsyncSession):
    async with state.proxy() as data:
        previous_page = int(data.get("previous_page"))
        feedback_num = int(data.get("feedback_num"))
        feedbacks_count = int(data.get("feedbacks_count"))
        top_msg_id = data.get("top_msg_id")

    current_page = callback_data.get("page")
    if current_page == "cancel":
        await call.answer()
        await call.message.bot.delete_message(chat_id=call.from_user.id, message_id=top_msg_id)
        await call.message.delete()
        await call.message.answer("Главное меню:", reply_markup=main_menu_kb)
        await state.reset_data()
        await state.reset_state()
        return
    elif current_page == "begin_empty":
        await call.answer("Вы в самом начале списка!", show_alert=False)
        return
    elif current_page == "end_empty":
        await call.answer("Вы достигли конца списка!", show_alert=False)
        return
    await call.answer()

    if previous_page > int(current_page):
        feedback_num -= 1
    else:
        feedback_num += 1

    feedback_obj = await feedback_functions.get_feedback(session, feedback_num=feedback_num)
    text = f"📨 Отзыв №{feedback_num}: \n{feedback_obj.feedback_text}"
    keyboard = feedbacks_kb(feedbacks_count=feedbacks_count, page=int(current_page))
    await call.message.edit_text(text=text, reply_markup=keyboard)
    await state.update_data(feedback_num=feedback_num, previous_page=current_page)


async def show_file_id(message: types.Message):
    await message.reply(message.photo[-1].file_id)


def register_admin_commands(dp: Dispatcher):
    dp.register_message_handler(get_bot_statistics, commands=["statistics"], is_admin=True, state="*")
    dp.register_message_handler(show_feedbacks, commands=["show_feedbacks"], is_admin=True, state="*")
    dp.register_callback_query_handler(show_chosen_page, feedbacks_pagination_call_cd.filter(),
                                       state=AdminActions.FeedbacksChecking)
    # dp.register_message_handler(show_file_id, content_types=types.ContentType.PHOTO, is_admin=True, state="*")
