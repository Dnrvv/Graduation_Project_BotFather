from typing import Union

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.infrastructure.database.db_functions import product_functions
from tgbot.keyboards.menu_inline_kbs import categories_keyboard, items_keyboard, \
    item_keyboard, cafe_menu_cd, order_products_cd, cart_keyboard
from tgbot.keyboards.reply_kbs import main_menu_kb
from tgbot.misc.states import Order
from tgbot.services.service_functions import number_to_emoji, format_number_with_spaces


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


async def show_item(call: types.CallbackQuery, category, product_id, state: FSMContext, session: AsyncSession):
    await call.answer()
    keyboard = await item_keyboard(category=category, product_id=int(product_id), session=session)
    user_id = call.from_user.id
    product_obj = await product_functions.get_product(session, product_id=int(product_id))
    text = (f"<b>{product_obj.product_name}</b>\n\n"
            f"{product_obj.product_caption}\n\n"
            f"Цена: {format_number_with_spaces(product_obj.product_price)} сум\n\n"
            f"Укажите количество:")
    photo = product_obj.photo_file_id
    await call.bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
    ph_msg = await call.bot.send_photo(photo=photo, chat_id=user_id, caption=text, reply_markup=keyboard)

    # СЛЕДИТЬ ЗА СЧЕТЧИКОМ!!!!!
    await state.update_data(ph_msg_id=ph_msg.message_id, menu_msg_id=None, quantity_counter=1)


async def change_product_quantity(call: types.CallbackQuery, callback_data: dict, state: FSMContext,
                                  session: AsyncSession):
    product_id = int(callback_data.get("product_id"))
    category = callback_data.get("category")
    quantity_counter = int(callback_data.get("quantity_counter"))

    if quantity_counter < 1:
        await call.answer("Минимальное количество - 1 шт.", show_alert=False)
        return

    elif quantity_counter > 100:
        await call.answer("Максимальное количество - 100 шт.", show_alert=False)
        return

    if product_id == "counter":
        await call.answer(f"Количество, которое Вы указали: {quantity_counter}", show_alert=False)
        return

    await call.answer()
    await state.update_data(quantity_counter=quantity_counter)
    await call.message.edit_reply_markup(reply_markup=await item_keyboard(category, product_id,
                                                                          session, quantity_counter))


async def add_product_to_cart(call: types.CallbackQuery, category, product_id, state: FSMContext, session: AsyncSession):
    # Тут будет взаимодействие с category и product_id (а именно - добавление в корзину)

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
    cart_text = "📥 <b>Корзина:</b>\n\n"
    total_products_cost = 0

    for product_id, quantity in selected_products.items():
        product_obj = await product_functions.get_product(session, product_id=int(product_id))

        cart_product_cost = quantity * product_obj.product_price
        total_products_cost += cart_product_cost

        cart_text += f"<b>{product_obj.product_name}</b>\n"
        cart_text += (f"<b> {number_to_emoji(quantity)}</b> ✖️ {format_number_with_spaces(product_obj.product_price)} "
                      f"= {format_number_with_spaces(cart_product_cost)} сум \n")

    cart_text += (f"\n<b>Продукты:</b> {format_number_with_spaces(total_products_cost)} сум\n"
                  f"<b>Доставка:</b> {format_number_with_spaces(delivery_cost)} сум\n"
                  f"<b>Итого: {format_number_with_spaces(total_products_cost + delivery_cost)} сум</b>")
    await state.update_data(total_products_cost=total_products_cost)
    await call.message.edit_text(text=cart_text, reply_markup=await cart_keyboard(category=category,
                                                                                  session=session))


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
    dp.register_callback_query_handler(change_product_quantity, order_products_cd.filter(), state=Order.Menu)
