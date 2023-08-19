from typing import Union

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.infrastructure.database.db_functions import product_functions
from tgbot.keyboards.generate_keyboards import categories_keyboard, subcategories_keyboard, items_keyboard, \
    item_keyboard, menu_callback
from tgbot.keyboards.reply_kbs import main_menu_kb
from tgbot.misc.states import Order


async def back_to_main_menu(call: types.CallbackQuery, state: FSMContext, category="0", subcategory="0", item_id="0"):
    await state.reset_data()
    await state.finish()
    await call.bot.edit_message_text(text="Главное меню:", chat_id=call.from_user.id,
                                     message_id=call.message.message_id, reply_markup=main_menu_kb)


async def list_categories(message: Union[types.Message, types.CallbackQuery], session: AsyncSession, **kwargs):
    markup = await categories_keyboard(session=session)
    if isinstance(message, types.Message):
        await message.answer("🔹 Выберите бренд:", reply_markup=markup)
    elif isinstance(message, types.CallbackQuery):
        call = message
        await call.message.edit_text(text="🔹 Выберите бренд:", reply_markup=markup)


async def list_subcategories(call: types.CallbackQuery, category, session: AsyncSession, **kwargs):
    markup = await subcategories_keyboard(category, session=session)
    await call.message.edit_text(text="🔹 Выберите категорию:", reply_markup=markup)


async def list_items(call: types.CallbackQuery, category, subcategory, session: AsyncSession, **kwargs):
    markup = await items_keyboard(category, subcategory, session=session)
    # await call.bot.delete_message(chat_id=call.from_user.id,
    #                               message_id=call.message.message_id)
    # await call.message.answer(text="🔹 Выберите продукт:",
    #                           reply_markup=markup)
    await call.message.edit_text(text="🔹 Выберите продукт:", reply_markup=markup)


async def show_item(call: types.CallbackQuery, category, subcategory, product_id, session: AsyncSession):
    markup = await item_keyboard(category=category, subcategory=subcategory, product_id=product_id, session=session)
    user_id = call.from_user.id
    product = await product_functions.get_product(session, product_id=product_id)
    text = (f"<b>{product.product_name}</b>\n\n"
            f"{product.product_caption}")
    photo = f"{product.photo_file_id}"
    await call.bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
    await call.bot.send_photo(photo=photo, chat_id=user_id, caption=text)
    await call.message.answer(text="🔹 Выберите действие:", reply_markup=markup)


async def global_navigate(call: types.CallbackQuery, callback_data: dict, session: AsyncSession):
    current_level = callback_data.get("level")
    category = callback_data.get("category")
    subcategory = callback_data.get("subcategory")
    product_id = callback_data.get("product_id")

    levels = {
        "-1": back_to_main_menu,
        "0": list_categories,
        "1": list_subcategories,
        "2": show_item
    }

    current_level_function = levels[current_level]

    await current_level_function(call, category=category,
                                 subcategory=subcategory, product_id=product_id, session=session)


def register_cafe_menu_navigation(dp: Dispatcher):
    dp.register_callback_query_handler(global_navigate, menu_callback.filter(), state=Order.Menu)
