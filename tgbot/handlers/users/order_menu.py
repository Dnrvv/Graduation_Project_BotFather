from typing import Union

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.infrastructure.database.db_functions import product_functions
from tgbot.keyboards.menu_inline_kbs import categories_keyboard, items_keyboard, \
    item_keyboard, cafe_menu_cd, order_products_cd, cart_keyboard, cart_products_cd
from tgbot.keyboards.reply_kbs import main_menu_kb
from tgbot.middlewares.throttling import rate_limit
from tgbot.misc.dependences import MAX_PRODUCT_IN_CART_QUANTITY
from tgbot.misc.states import Order
from tgbot.services.text_formatting_functions import create_cart_text
from tgbot.services.service_functions import format_number_with_spaces


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
        await call.answer()
        await call.message.edit_text(text="🍴 Выберите категорию:", reply_markup=keyboard)


async def list_items(call: types.CallbackQuery, category, state: FSMContext, session: AsyncSession, **kwargs):
    await call.answer()
    async with state.proxy() as data:
        ph_msg_id = data.get("ph_msg_id")
    keyboard = await items_keyboard(category, session=session)
    if ph_msg_id:
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=ph_msg_id)
        menu_msg = await call.message.answer(text="😋 Выберите продукт:", reply_markup=keyboard)
        await state.update_data(ph_msg_id=None, menu_msg_id=menu_msg.message_id)
        return

    await call.message.edit_text(text="😋 Выберите продукт:", reply_markup=keyboard)


async def show_item(message: Union[types.Message, types.CallbackQuery], category, product_id, state: FSMContext,
                    session: AsyncSession):
    keyboard = await item_keyboard(category=category, product_id=int(product_id), session=session)
    product_obj = await product_functions.get_product(session, product_id=int(product_id))
    text = (f"<b>{product_obj.product_name}</b>\n\n"
            f"{product_obj.product_caption}\n\n"
            f"Цена: {format_number_with_spaces(product_obj.product_price)} сум\n\n"
            f"Укажите количество:")
    photo = product_obj.photo_file_id
    ph_msg = None
    if isinstance(message, types.Message):
        user_id = message.from_user.id
        ph_msg = await message.bot.send_photo(photo=photo, chat_id=user_id, caption=text, reply_markup=keyboard)

    elif isinstance(message, types.CallbackQuery):
        call = message
        await call.answer()
        user_id = call.from_user.id
        await call.bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
        ph_msg = await call.bot.send_photo(photo=photo, chat_id=user_id, caption=text, reply_markup=keyboard)

    await state.update_data(ph_msg_id=ph_msg.message_id, menu_msg_id=None, quantity_counter=1)


async def change_product_quantity(call: types.CallbackQuery, callback_data: dict, state: FSMContext,
                                  session: AsyncSession):
    product_id = int(callback_data.get("product_id"))
    category = callback_data.get("category")
    quantity_counter = int(callback_data.get("quantity_counter"))

    if quantity_counter < 1:
        await call.answer("Минимальное количество - 1 шт.", show_alert=False)
        return

    elif quantity_counter > MAX_PRODUCT_IN_CART_QUANTITY:
        await call.answer(f"Максимальное количество - {MAX_PRODUCT_IN_CART_QUANTITY} шт.", show_alert=False)
        return

    if product_id == "counter":
        await call.answer(f"Количество, которое Вы указали: {quantity_counter}", show_alert=False)
        return

    await call.answer()
    await state.update_data(quantity_counter=quantity_counter)
    await call.message.edit_reply_markup(reply_markup=await item_keyboard(category, product_id,
                                                                          session, quantity_counter))


async def choose_product_inline_query(query: types.InlineQuery, session: AsyncSession):
    if len(query.query) >= 2:
        search_text = query.query
        products_list = await product_functions.get_products_via_query(session, search_text=search_text)
    else:
        products_list = await product_functions.get_products(session)
    results = []
    for product in products_list:
        results.append(types.InlineQueryResultArticle(
            id=f"{product.product_id}",
            thumb_url=f"{product.photo_web_link}",
            title=f"{product.product_name}",

            description=f"{format_number_with_spaces(product.product_price)} сум",
            input_message_content=types.InputTextMessageContent(
                message_text=f"{product.product_name}",
                parse_mode="HTML"
            ),
        ))
    await query.answer(cache_time=5, is_personal=True, results=results)


@rate_limit(1)
async def show_item_via_inline_query(message: types.Message, state: FSMContext, session: AsyncSession):
    product_name = message.text
    product_obj = await product_functions.get_product_by_name(session, product_name=product_name)
    if not product_obj:
        await message.answer("Ошибка. Такого товара нет.")
        return
    async with state.proxy() as data:
        menu_msg_id = data.get("menu_msg_id")
        ph_msg_id = data.get("ph_msg_id")

    if menu_msg_id:
        await message.bot.delete_message(chat_id=message.from_user.id, message_id=menu_msg_id)
        await state.update_data(menu_msg_id=None)
    if ph_msg_id:
        await message.bot.delete_message(chat_id=message.from_user.id, message_id=ph_msg_id)
        await state.update_data(ph_msg_id=None)

    await show_item(message, category=product_obj.category_code, product_id=product_obj.product_id,
                    state=state, session=session)


async def add_product_to_cart(call: types.CallbackQuery, category, product_id, state: FSMContext, session: AsyncSession):
    async with state.proxy() as data:
        quantity_counter = data.get("quantity_counter")
        selected_products = data.get("selected_products", {})
        selected_products[product_id] = selected_products.get(product_id, 0) + quantity_counter
        data["selected_products"] = selected_products

    await call.answer(f"Добавлено в корзину {quantity_counter} шт.", show_alert=False)
    await call.message.delete()

    keyboard = await categories_keyboard(session=session)
    menu_msg = await call.message.answer("🍴 Выберите категорию:", reply_markup=keyboard)
    await state.update_data(ph_msg_id=None, menu_msg_id=menu_msg.message_id, quantity_counter=1)


async def show_cart(call: types.CallbackQuery, category, product_id, state: FSMContext, session: AsyncSession):
    async with state.proxy() as data:
        selected_products = data.get("selected_products", {})
        delivery_cost = data.get("delivery_cost")

    if not selected_products:
        await call.answer("Ваша корзина пуста!", show_alert=False)
        return

    await call.answer()
    cart_text, total_products_cost = await create_cart_text(selected_products=selected_products,
                                                            delivery_cost=delivery_cost, session=session)
    await state.update_data(total_products_cost=total_products_cost)
    await call.message.edit_text(text=cart_text, reply_markup=await cart_keyboard(category=category, session=session,
                                                                                  selected_products=selected_products))


async def change_cart_products_quantity(call: types.CallbackQuery, callback_data: dict, state: FSMContext,
                                        session: AsyncSession):
    product_id = int(callback_data.get("product_id"))
    category = callback_data.get("category")
    product_quantity = int(callback_data.get("product_quantity"))
    async with state.proxy() as data:
        delivery_cost = data.get("delivery_cost")
        selected_products = data.get("selected_products", {})

    if product_quantity <= 0:
        await call.answer()
        del selected_products[product_id]

    elif product_quantity > MAX_PRODUCT_IN_CART_QUANTITY:
        await call.answer(f"Максимальное количество - {MAX_PRODUCT_IN_CART_QUANTITY} шт.", show_alert=False)
        return

    elif product_id == "product_name":
        await call.answer(f"Количество, которое Вы указали: {product_quantity}", show_alert=False)
        return

    elif product_quantity > 0:
        await call.answer()
        selected_products[product_id] = product_quantity

    if not selected_products:
        await state.update_data(selected_products=selected_products, total_products_cost=0)
        await list_categories(call, state=state, session=session)
        return

    cart_text, total_products_cost = await create_cart_text(selected_products=selected_products,
                                                            delivery_cost=delivery_cost, session=session)
    await call.message.edit_text(text=cart_text, reply_markup=await cart_keyboard(category=category, session=session,
                                                                                  selected_products=selected_products))

    await state.update_data(selected_products=selected_products, total_products_cost=total_products_cost)


async def global_navigate(call: types.CallbackQuery, callback_data: dict, state: FSMContext, session: AsyncSession):
    current_level = callback_data.get("level")
    category = callback_data.get("category")
    product_id = int(callback_data.get("product_id"))

    levels = {
        "-1": back_to_main_menu,
        "0": list_categories,
        "1": list_items,
        "2": show_item,
        "3": add_product_to_cart,
        "4": show_cart
    }

    current_level_function = levels[current_level]

    await current_level_function(call, category=category, product_id=product_id, state=state,
                                 session=session)


def register_order_menu(dp: Dispatcher):
    dp.register_callback_query_handler(global_navigate, cafe_menu_cd.filter(), state=Order.Menu)

    dp.register_inline_handler(choose_product_inline_query, state=Order.Menu)
    dp.register_message_handler(show_item_via_inline_query, state=Order.Menu)

    dp.register_callback_query_handler(change_product_quantity, order_products_cd.filter(), state=Order.Menu)
    dp.register_callback_query_handler(change_cart_products_quantity, cart_products_cd.filter(), state=Order.Menu)
