from typing import Union

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.infrastructure.database.db_functions import product_functions
from tgbot.keyboards.generate_keyboards import categories_keyboard, items_keyboard, \
    item_keyboard, cafe_menu_cd
from tgbot.keyboards.reply_kbs import main_menu_kb
from tgbot.misc.states import Order


async def back_to_main_menu(call: types.CallbackQuery, state: FSMContext, session: AsyncSession,
                            category="0", product_id="0"):
    await state.reset_data()
    await state.finish()
    await call.bot.edit_message_text(text="Главное меню:", chat_id=call.from_user.id,
                                     message_id=call.message.message_id, reply_markup=main_menu_kb)


async def list_categories(message: Union[types.Message, types.CallbackQuery], state: FSMContext,
                          session: AsyncSession, **kwargs):
    keyboard = await categories_keyboard(session=session)
    if isinstance(message, types.Message):
        menu_msg = await message.answer("🍴 Выберите категорию:", reply_markup=keyboard)
        await state.update_data(menu_msg_id=menu_msg.message_id)
    elif isinstance(message, types.CallbackQuery):
        call = message
        await call.message.edit_text(text="🍴 Выберите категорию:", reply_markup=keyboard)


async def list_items(call: types.CallbackQuery, category, state: FSMContext, session: AsyncSession, **kwargs):
    data = await state.get_data()
    ph_msg_id = data.get("ph_msg_id")
    keyboard = await items_keyboard(category, session=session)
    if ph_msg_id:
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=ph_msg_id)
        menu_msg = await call.message.answer(text="😋 Выберите продукт:", reply_markup=keyboard)
        await state.update_data(ph_msg_id=None, menu_msg_id=menu_msg.message_id)
        return

    # await call.bot.delete_message(chat_id=call.from_user.id,
    #                               message_id=call.message.message_id)
    # await call.message.answer(text="🔹 Выберите продукт:",
    #                           reply_markup=keyboard)
    await call.message.edit_text(text="😋 Выберите продукт:", reply_markup=keyboard)


async def show_item(call: types.CallbackQuery, category, product_id, state: FSMContext, session: AsyncSession):
    keyboard = await item_keyboard(category=category, product_id=product_id, session=session)
    user_id = call.from_user.id
    product = await product_functions.get_product(session, product_id=product_id)
    text = (f"<b>{product.product_name}</b>\n\n"
            f"{product.product_caption}\n\n"
            f"Укажите количество:")
    photo = f"{product.photo_file_id}"
    await call.bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
    ph_msg = await call.bot.send_photo(photo=photo, chat_id=user_id, caption=text, reply_markup=keyboard)
    # menu_msg = await call.message.answer(text="Укажите количество:", reply_markup=keyboard)
    # menu_msg_id = menu_msg.message_id
    await state.update_data(ph_msg_id=ph_msg.message_id, menu_msg_id=None)


async def add_to_cart(call: types.CallbackQuery, category, product_id, state: FSMContext, session: AsyncSession):
    # Тут будет взаимодействие с category и product_id (а именно - добавление в корзину)
    await call.answer("Добавлено в корзину", show_alert=False)
    await call.message.delete()
    keyboard = await categories_keyboard(session=session)
    menu_msg = await call.message.answer("🍴 Выберите категорию:", reply_markup=keyboard)
    await state.update_data(ph_msg_id=None, menu_msg_id=menu_msg.message_id)


async def global_navigate(call: types.CallbackQuery, callback_data: dict, state: FSMContext, session: AsyncSession):
    current_level = callback_data.get("level")
    category = callback_data.get("category")
    product_id = callback_data.get("product_id")

    levels = {
        "-1": back_to_main_menu,
        "0": list_categories,
        "1": list_items,
        "2": show_item,
        "3": add_to_cart
    }

    current_level_function = levels[current_level]

    await current_level_function(call, category=category,
                                 product_id=product_id, state=state, session=session)


def register_cafe_menu_navigation(dp: Dispatcher):
    dp.register_callback_query_handler(global_navigate, cafe_menu_cd.filter(), state=Order.Menu)
