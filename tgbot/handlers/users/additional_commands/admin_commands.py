from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.infrastructure.database.db_functions import settings_functions, user_functions, order_functions
from tgbot.middlewares.throttling import rate_limit
from tgbot.misc.states import AdminActions


@rate_limit(1)
async def get_bot_statistics(message: types.Message, session: AsyncSession):
    users_count = await user_functions.get_users_count(session)
    orders_count = await order_functions.get_orders_count(session)
    await message.answer(f"📑 Статистика:\n"
                         f"• Зарегистрировано пользователей: <b>{users_count}</b> чел.\n"
                         f"• Сделано заказов: <b>{orders_count}</b> шт.")


async def get_tou_file_id(message: types.Message):
    await message.answer("📨 Отправьте файл с пользовательским соглашением, чтобы обновить таковой в боте:")
    await AdminActions.GetTOUFile.set()


async def save_file_id(message: types.Message, state: FSMContext, session: AsyncSession):
    await settings_functions.update_tou_file_id(session, file_id=message.document.file_id)
    await session.commit()
    await message.answer("✅ Пользовательское соглашение <b>обновлено</b>.")
    await state.reset_data()
    await state.finish()


async def show_file_id(message: types.Message):
    await message.reply(message.photo[-1].file_id)


def register_admin_commands(dp: Dispatcher):
    dp.register_message_handler(get_bot_statistics, commands=["statistics"], is_admin=True, state="*")
    dp.register_message_handler(get_tou_file_id, commands=["update_tou"], is_admin=True, state="*")
    dp.register_message_handler(save_file_id, content_types=types.ContentType.DOCUMENT, is_admin=True,
                                state=AdminActions.GetTOUFile)
    dp.register_message_handler(show_file_id, content_types=types.ContentType.PHOTO, is_admin=True,
                                state="*")
