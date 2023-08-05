from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.markdown import quote_html
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.infrastructure.database.db_functions import user_functions
from tgbot.infrastructure.database.db_functions.settings_functions import update_active_users_count
from tgbot.keyboards.inline_kbs import notify_users_approve_kb, notify_users_approve_callback, notify_users_approves
from tgbot.keyboards.reply_kbs import main_menu_kb
from tgbot.middlewares.throttling import rate_limit
from tgbot.misc.states import NotifyUsers
from tgbot.services.broadcast_functions import *


@rate_limit(1, key="commands")
async def notify_users(message: types.Message):
    await message.answer("📦 Отправьте текст/фото/файл для оповещения пользователей:",
                         reply_markup=ReplyKeyboardRemove())
    await NotifyUsers.GetNotifyMedia.set()


@rate_limit(2, key="notify_users")
async def get_notify_media(message: types.Message, state: FSMContext):
    await message.answer("📬 Пользователям придёт следующее уведомление:")

    if not message.caption and not message.text:
        text_to_send = "💬 Сообщение от администратора."
    elif message.caption:
        text_to_send = f"💬 Сообщение от администратора:\n\n{message.caption}"
    else:
        text_to_send = f"💬 Сообщение от администратора:\n\n{message.text}"

    if message.text:
        await message.answer(quote_html(text_to_send))
        await state.update_data(msg_type="text", text=text_to_send)

    elif message.photo:
        await message.answer_photo(photo=message.photo[-1].file_id, caption=quote_html(text_to_send))
        await state.update_data(msg_type="photo", photo_id=message.photo[-1].file_id, caption=text_to_send)

    elif message.document:
        await message.answer_document(document=message.document.file_id, caption=quote_html(text_to_send))
        await state.update_data(msg_type="document", document_id=message.document.file_id, caption=text_to_send)

    elif message.sticker:
        await message.answer_sticker(sticker=message.sticker.file_id)
        await state.update_data(msg_type="sticker", sticker_id=message.sticker.file_id)

    elif message.audio:
        await message.answer_audio(audio=message.audio.file_id)
        await state.update_data(msg_type="audio", audio_id=message.audio.file_id, caption=text_to_send)

    elif message.animation:
        await message.answer_animation(animation=message.animation.file_id)
        await state.update_data(msg_type="animation", animation_id=message.audio.file_id, caption=text_to_send)

    else:
        await message.answer("❗️ Бот может рассылать только текст, фото, файлы, музыку, гифки и стикеры.")
        return

    await message.answer("Подтвердите отправку:", reply_markup=notify_users_approve_kb)
    await NotifyUsers.NotifyApprove.set()


async def notify_approve(call: types.CallbackQuery, callback_data: dict, state: FSMContext, session: AsyncSession):
    await call.answer()
    approve = callback_data.get("approve")
    if approve == "send":
        data = await state.get_data()
        users = await user_functions.get_some_users(session)
        msg_type = data.get("msg_type")

        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="✅ Бот начал рассылку.")
        await call.message.answer("Главное меню:", reply_markup=main_menu_kb)
        counter = 0

        if msg_type == "text":
            text = data.get("text")
            try:
                for user in users:
                    if await send_text(bot=call.bot, user_id=user.telegram_id, text=quote_html(text),
                                       disable_notification=True):
                        counter += 1
                    await asyncio.sleep(0.1)
            finally:
                await call.message.answer(f"📬 Успешно отправлено сообщений: {counter}")
                logging.info(f"Successfully sent messages: {counter}")

        elif msg_type == "photo":
            photo_id = data.get("photo_id")
            caption = data.get("caption")
            try:
                for user in users:
                    if await send_photo(bot=call.bot, user_id=user.telegram_id, photo_id=photo_id,
                                        caption=quote_html(caption), disable_notification=True):
                        counter += 1
                    await asyncio.sleep(0.1)
            finally:
                await call.message.answer(f"📬 Успешно отправлено сообщений: {counter}")
                logging.info(f"Successfully sent messages: {counter}")

        elif msg_type == "document":
            document_id = data.get("document_id")
            caption = data.get("caption")
            try:
                for user in users:
                    if await send_document(bot=call.bot, user_id=user.telegram_id, document_id=document_id,
                                           caption=quote_html(caption), disable_notification=True):
                        counter += 1
                    await asyncio.sleep(0.1)
            finally:
                await call.message.answer(f"📬 Успешно отправлено сообщений: {counter}")
                logging.info(f"Successfully sent messages: {counter}")

        elif msg_type == "audio":
            caption = data.get("caption")
            audio_id = data.get("audio_id")
            try:
                for user in users:
                    if await send_audio(bot=call.bot, user_id=user.telegram_id, audio_id=audio_id,
                                        caption=quote_html(caption), disable_notification=True):
                        counter += 1
                    await asyncio.sleep(0.1)
            finally:
                await call.message.answer(f"📬 Успешно отправлено сообщений: {counter}")
                logging.info(f"Successfully sent messages: {counter}")

        elif msg_type == "animation":
            caption = data.get("caption")
            animation_id = data.get("animation_id")
            try:
                for user in users:
                    if await send_animation(bot=call.bot, user_id=user.telegram_id, animation_id=animation_id,
                                            caption=quote_html(caption), disable_notification=True):
                        counter += 1
                    await asyncio.sleep(0.1)
            finally:
                await call.message.answer(f"📬 Успешно отправлено сообщений: {counter}")
                logging.info(f"Successfully sent messages: {counter}")

        elif msg_type == "sticker":
            sticker_id = data.get("sticker_id")
            try:
                for user in users:
                    if await send_sticker(bot=call.bot, user_id=user.telegram_id, sticker_id=sticker_id,
                                          disable_notification=True):
                        counter += 1
                    await asyncio.sleep(0.1)
            finally:
                await call.message.answer(f"📬 Успешно отправлено сообщений: {counter}")
                logging.info(f"Successfully sent messages: {counter}")

        await update_active_users_count(session=session, count=counter)
        await session.commit()

    elif approve == "cancel":
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="❌ Рассылка отменена.")
        await call.message.answer("Главное меню:", reply_markup=main_menu_kb)

    await state.reset_data()
    await state.finish()


def register_notify_users(dp: Dispatcher):
    dp.register_message_handler(notify_users, commands=["notify_users"], is_admin=True, state="*")
    dp.register_message_handler(get_notify_media, content_types=types.ContentType.ANY, is_admin=True,
                                state=NotifyUsers.GetNotifyMedia)
    dp.register_callback_query_handler(notify_approve,
                                       notify_users_approve_callback.filter(approve=notify_users_approves),
                                       is_admin=True, state=NotifyUsers.NotifyApprove)
