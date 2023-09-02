from typing import Union

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.infrastructure.database.db_functions import product_functions
from tgbot.infrastructure.database.db_models.order_models import Product
from tgbot.keyboards.moderation_menu_kbs import moderation_mm_kb, moderation_mm_cd, moderation_mm_actions, \
    moderation_categories_kb, moderation_items_kb, moderation_item_kb, moderation_menu_cd, product_moderation_cd
from tgbot.keyboards.reply_kbs import reply_approve_kb, main_menu_kb, reply_cancel_kb
from tgbot.middlewares.throttling import rate_limit
from tgbot.misc.dependences import PRODUCT_NAME_LENGTH, PRODUCT_CAPTION_LENGTH
from tgbot.misc.states import ModerationActions
from tgbot.services.parse_functions import parse_edited_product
from tgbot.services.service_functions import format_number_with_spaces


@rate_limit(1)
async def get_moderation_menu(message: Union[types.Message, types.CallbackQuery], state: FSMContext,
                              session: AsyncSession, category="0", product_id="0"):
    if isinstance(message, types.Message):
        await message.answer("⚙️ Выберите действие:", reply_markup=moderation_mm_kb)
    elif isinstance(message, types.CallbackQuery):
        call = message
        await call.answer()
        await call.message.edit_text("⚙️ Выберите действие:", reply_markup=moderation_mm_kb)
    await state.reset_data()
    await ModerationActions.GetAction.set()


async def get_moderation_action(call: types.CallbackQuery, callback_data: dict, state: FSMContext,
                                session: AsyncSession):
    await call.answer()
    action = callback_data.get("action")
    if action == "cancel":
        await call.message.delete()
        await call.message.answer("Главное меню:", reply_markup=main_menu_kb)
        await state.reset_data()
        await state.finish()
    elif action == "add_product":
        await call.message.delete()
        await call.message.answer("Отправьте фото продукта:", reply_markup=reply_cancel_kb)
        await ModerationActions.GetProductPhoto.set()
    elif action == "edit_product":
        await list_categories(call, state, session)
        await ModerationActions.ProductsMenu.set()


async def list_categories(message: Union[types.Message, types.CallbackQuery], state: FSMContext,
                          session: AsyncSession, **kwargs):
    keyboard = await moderation_categories_kb(session=session)
    if isinstance(message, types.Message):
        menu_msg = await message.answer("Выберите категорию:", reply_markup=keyboard)
        await state.update_data(menu_msg_id=menu_msg.message_id)
    elif isinstance(message, types.CallbackQuery):
        call = message
        await call.answer()
        await call.message.edit_text(text="Выберите категорию:", reply_markup=keyboard)


async def list_items(call: types.CallbackQuery, category, state: FSMContext, session: AsyncSession, **kwargs):
    await call.answer()
    async with state.proxy() as data:
        ph_msg_id = data.get("ph_msg_id")
    keyboard = await moderation_items_kb(category, session=session)
    if ph_msg_id:
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=ph_msg_id)
        menu_msg = await call.message.answer(text="Выберите продукт:", reply_markup=keyboard)
        await state.update_data(ph_msg_id=None, menu_msg_id=menu_msg.message_id)
        return

    await call.message.edit_text(text="Выберите продукт:", reply_markup=keyboard)


async def show_item(call: types.CallbackQuery, category, product_id, state: FSMContext, session: AsyncSession):
    await call.answer()
    keyboard = await moderation_item_kb(category=category, product_id=int(product_id), session=session)
    user_id = call.from_user.id
    product_obj = await product_functions.get_product(session, product_id=int(product_id))
    text = (f"Название: <b>{product_obj.product_name}</b>\n\n"
            f"Описание: {product_obj.product_caption}\n\n"
            f"Цена: {format_number_with_spaces(product_obj.product_price)} сум\n\n"
            f"<b>Что Вы хотите редактировать?</b>")
    photo = product_obj.photo_file_id
    await call.bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
    ph_msg = await call.bot.send_photo(photo=photo, chat_id=user_id, caption=text, reply_markup=keyboard)

    await state.update_data(ph_msg_id=ph_msg.message_id, menu_msg_id=None)


async def moderation_menu_navigate(call: types.CallbackQuery, callback_data: dict, state: FSMContext, session: AsyncSession):
    current_level = callback_data.get("level")
    category = callback_data.get("category")
    product_id = callback_data.get("product_id")

    levels = {
        "-1": get_moderation_menu,
        "0": list_categories,
        "1": list_items,
        "2": show_item,
    }

    current_level_function = levels[current_level]

    await current_level_function(call, category=category, product_id=product_id, state=state,
                                 session=session)


async def get_item_action(call: types.CallbackQuery, callback_data: dict, state: FSMContext,
                          session: AsyncSession):
    await call.answer()
    await call.message.delete()
    action = callback_data.get("action")
    product_id = callback_data.get("product_id")
    await state.update_data(product_id=product_id, action=action)

    if action == "edit_photo":
        await call.message.answer("Отправьте новое <b>фото</b> продукта (не файлом!):", reply_markup=reply_cancel_kb)
    elif action == "edit_name":
        await call.message.answer(f"Отправьте новое <b>название</b> продукта (максимум "
                                  f"{PRODUCT_NAME_LENGTH} символов):", reply_markup=reply_cancel_kb)
    elif action == "edit_caption":
        await call.message.answer(f"Отправьте новое <b>описание</b> продукта (максимум "
                                  f"{PRODUCT_CAPTION_LENGTH} символов):", reply_markup=reply_cancel_kb)
    elif action == "edit_price":
        await call.message.answer("Отправьте новую <b>цену</b> продукта (целочисленное значение, например: 24000 или "
                                  "24500):", reply_markup=reply_cancel_kb)
    elif action == "hide_product":
        product_obj = await product_functions.get_product(session, product_id=int(product_id))
        await call.message.answer(f"Скрыть продукт <b>{product_obj.product_name}</b>?",
                                  reply_markup=reply_approve_kb)
        await ModerationActions.EditProductApprove.set()
        return
    elif action == "reveal_product":
        product_obj = await product_functions.get_product(session, product_id=int(product_id))
        await call.message.answer(f"Восстановить продукт <b>{product_obj.product_name}</b>?",
                                  reply_markup=reply_approve_kb)
        await ModerationActions.EditProductApprove.set()
        return

    await ModerationActions.EditProduct.set()


async def get_new_product_parameter(message: types.Message, state: FSMContext, session: AsyncSession):
    async with state.proxy() as data:
        product_id = data.get("product_id")
        action = data.get("action")

    if action == "edit_photo":
        if message.document:
            await message.answer("❗️ Отправьте фото не файлом.")
            return
        caption = await parse_edited_product(product_id=int(product_id), session=session)
        caption += "💾 <b>Сохранить изменения?</b>"
        await message.answer_photo(photo=message.photo[-1].file_id, caption=caption, reply_markup=reply_approve_kb)
        await state.update_data(photo_file_id=message.photo[-1].file_id)

    elif action == "edit_name":
        if len(message.text) > PRODUCT_NAME_LENGTH:
            await message.answer(f"❗️ Длина названия продукта должна составлять не более "
                                 f"{PRODUCT_NAME_LENGTH} символов!")
            return
        caption = await parse_edited_product(product_id=int(product_id), session=session, product_name=message.text)
        caption += "💾 <b>Сохранить изменения?</b>"
        old_product_obj = await product_functions.get_product(session, product_id=int(product_id))
        await message.answer_photo(photo=old_product_obj.photo_file_id, caption=caption, reply_markup=reply_approve_kb)
        await state.update_data(product_name=message.text)

    elif action == "edit_caption":
        if len(message.text) > PRODUCT_CAPTION_LENGTH:
            await message.answer(f"❗️ Длина описания продукта должна составлять не более {PRODUCT_CAPTION_LENGTH}"
                                 f" символов!")
            return
        caption = await parse_edited_product(product_id=int(product_id), session=session, product_caption=message.text)
        caption += "💾 <b>Сохранить изменения?</b>"
        old_product_obj = await product_functions.get_product(session, product_id=int(product_id))
        await message.answer_photo(photo=old_product_obj.photo_file_id, caption=caption, reply_markup=reply_approve_kb)
        await state.update_data(product_caption=message.text)

    elif action == "edit_price":
        if not message.text.isdigit() or isinstance(message.text, float):
            await message.answer("❗️ Введите целочисленное значение!")
            return
        caption = await parse_edited_product(product_id=int(product_id), session=session,
                                             product_price=int(message.text))
        caption += "💾 <b>Сохранить изменения?</b>"
        old_product_obj = await product_functions.get_product(session, product_id=int(product_id))
        await message.answer_photo(photo=old_product_obj.photo_file_id, caption=caption, reply_markup=reply_approve_kb)
        await state.update_data(product_price=message.text)

    await ModerationActions.EditProductApprove.set()


async def edit_product_approve(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == "✅ Да":
        async with state.proxy() as data:
            product_id = int(data.get("product_id"))
            action = data.get("action")

        if action == "edit_photo":
            photo_file_id = data.get("photo_file_id")
            await product_functions.update_product(session, Product.product_id == product_id,
                                                   photo_file_id=photo_file_id)
        elif action == "edit_name":
            product_name = data.get("product_name")
            await product_functions.update_product(session, Product.product_id == product_id,
                                                   product_name=product_name)
        elif action == "edit_caption":
            product_caption = data.get("product_caption")
            await product_functions.update_product(session, Product.product_id == product_id,
                                                   product_caption=product_caption)
        elif action == "edit_price":
            product_price = int(data.get("product_price"))
            await product_functions.update_product(session, Product.product_id == product_id,
                                                   product_price=product_price)

        elif action == "hide_product":
            await product_functions.update_product(session, Product.product_id == product_id, is_hidden=True)

        elif action == "reveal_product":
            await product_functions.update_product(session, Product.product_id == product_id, is_hidden=False)

        await session.commit()
        await message.answer("✅ Изменения применены.", reply_markup=ReplyKeyboardRemove())

    elif message.text == "❌ Нет":
        await message.answer("❌ Действие отменено.", reply_markup=ReplyKeyboardRemove())

    else:
        await message.answer("Используйте кнопки ниже:", reply_markup=reply_approve_kb)
        return

    await state.reset_data()
    await message.answer("⚙️ Выберите действие:", reply_markup=moderation_mm_kb)
    await ModerationActions.GetAction.set()


async def cancel_moderation(message: types.Message, state: FSMContext):
    await state.reset_data()
    await state.finish()
    await message.answer("Действие отменено.", reply_markup=main_menu_kb)


def register_moderation_menu(dp: Dispatcher):
    dp.register_message_handler(get_moderation_menu, commands=["moderation_menu"], is_admin=True, state="*")
    dp.register_message_handler(cancel_moderation, text="❌ Отмена", is_admin=True,
                                state=[ModerationActions.GetAction, ModerationActions.ProductsMenu,
                                       ModerationActions.EditProduct, ModerationActions.EditProductApprove])
    dp.register_callback_query_handler(get_moderation_action, moderation_mm_cd.filter(action=moderation_mm_actions),
                                       is_admin=True, state=ModerationActions.GetAction)

    dp.register_callback_query_handler(moderation_menu_navigate, moderation_menu_cd.filter(), is_admin=True,
                                       state=ModerationActions.ProductsMenu)
    dp.register_callback_query_handler(get_item_action, product_moderation_cd.filter(),
                                       state=ModerationActions.ProductsMenu)

    dp.register_message_handler(get_new_product_parameter, content_types=[types.ContentType.TEXT,
                                                                          types.ContentType.PHOTO],
                                state=ModerationActions.EditProduct)
    dp.register_message_handler(edit_product_approve, content_types=types.ContentType.TEXT, is_admin=True,
                                state=ModerationActions.EditProductApprove)
