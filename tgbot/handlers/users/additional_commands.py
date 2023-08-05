from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.infrastructure.database.db_functions import settings_functions
from tgbot.middlewares.throttling import rate_limit
from tgbot.misc.dependences import SUPPORT_USERNAME
from tgbot.misc.states import AdminActions


@rate_limit(3)
async def get_help(message: types.Message):
    await message.answer("🛠 Если что-то пошло не так, нажмите <b>/start</b>, чтобы перезапустить бота. "
                         f"Пожалуйста, сообщите об ошибке разработчику: <b>{SUPPORT_USERNAME}</b>")


async def get_tou_file_id(message: types.Message):
    await message.answer("📨 Отправьте файл с пользовательским соглашением, чтобы обновить таковой в боте:")
    await AdminActions.GetFile.set()


async def save_file_id(message: types.Message, state: FSMContext, session: AsyncSession):
    await settings_functions.update_tou_file_id(session, file_id=message.document.file_id)
    await session.commit()
    await message.answer("✅ Пользовательское соглашение <b>обновлено</b>.")
    await state.reset_data()
    await state.finish()


def register_additional_commands(dp: Dispatcher):
    dp.register_message_handler(get_help, commands=["help"], state="*")

    dp.register_message_handler(get_tou_file_id, commands=["update_tou"], is_admin=True, state="*")
    dp.register_message_handler(save_file_id, content_types=types.ContentType.DOCUMENT, is_admin=True,
                                state=AdminActions.GetFile)

