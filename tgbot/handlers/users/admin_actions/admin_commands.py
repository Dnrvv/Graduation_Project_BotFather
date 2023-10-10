from aiogram import Dispatcher, types

from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.infrastructure.database.db_functions import user_functions, order_functions
from tgbot.middlewares.throttling import rate_limit


@rate_limit(1)
async def get_bot_statistics(message: types.Message, session: AsyncSession):
    users_count = await user_functions.get_users_count(session)
    orders_count = await order_functions.get_orders_count(session)
    await message.answer(f"📑 Статистика:\n"
                         f"• Зарегистрировано пользователей: <b>{users_count}</b> чел.\n"
                         f"• Сделано заказов: <b>{orders_count}</b> шт.")


async def show_file_id(message: types.Message):
    await message.reply(message.photo[-1].file_id)


def register_admin_commands(dp: Dispatcher):
    dp.register_message_handler(get_bot_statistics, commands=["statistics"], is_admin=True, state="*")
    # dp.register_message_handler(show_file_id, content_types=types.ContentType.PHOTO, is_admin=True, state="*")
