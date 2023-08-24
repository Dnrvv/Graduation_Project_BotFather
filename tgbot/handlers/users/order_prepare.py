import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageToDeleteNotFound
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.config import load_config
from tgbot.handlers.users.cafe_menu_navigation import list_categories
from tgbot.infrastructure.database.db_functions import user_functions
from tgbot.keyboards.reply_kbs import delivery_location_kb, main_menu_kb, order_type_kb, saved_locations_kb, \
    reply_approve_kb, reply_cancel_kb
from tgbot.middlewares.throttling import rate_limit
from tgbot.misc.dependences import KM_DELIVERY_PRICE
from tgbot.misc.states import Order
from tgbot.services.address_request import get_address
from tgbot.services.broadcast_functions import broadcast
from tgbot.services.service_functions import calc_delivery_cost


@rate_limit(1)
async def get_order_type(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == "🛵 Доставка":
        await state.update_data(order_type="delivery")

        flag = await user_functions.check_user_addresses(session, cust_telegram_id=message.from_user.id)
        if flag:
            await message.answer("📍 Отправьте геопозицию или выберите адрес из сохранённых:",
                                 reply_markup=delivery_location_kb(has_addresses=flag))
        else:
            await message.answer("📍 Отправьте геопозицию:", reply_markup=delivery_location_kb(has_addresses=flag))

        await Order.GetLocation.set()
    elif message.text == "🚶 Самовывоз":
        await state.update_data(order_type="pickup")

        await message.answer("Вы выбрали самовывоз... Пока это в разработке...")

    elif message.text == "❌ Отмена":
        await message.answer("❌ Заказ отменён.", reply_markup=main_menu_kb)
        await state.reset_data()
        await state.finish()
    else:
        await message.answer("Некорректный ввод. Используйте кнопки ниже:", reply_markup=order_type_kb)


@rate_limit(1)
async def choose_saved_delivery_location(message: types.Message, session: AsyncSession):
    addresses = await user_functions.get_user_addresses(session, cust_telegram_id=message.from_user.id)
    await message.answer("Выберите адрес доставки:", reply_markup=saved_locations_kb(addresses=addresses))
    # await Order.GetLocation.set()


@rate_limit(1)
async def get_delivery_location(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.location:
        location = message.location
        address = await get_address(location.latitude, location.longitude)

        if not address:
            admins = load_config().tg_bot.admin_ids
            await broadcast(message.bot, users=admins, text=f"🛠 Ошибка при кодировке адреса.")

            await message.answer("Упс, что-то пошло не так... Администрация уже работает над этим.",
                                 reply_markup=main_menu_kb)
            await state.reset_data()
            await state.finish()
            return

        elif address == -1:
            await message.answer("😔 По указанному адресу служба доставки не работает. Попробуйте ещё раз:")
            return

        await message.answer(f"📍 Адрес, по которому будет доставлен заказ: <b>{address}</b>.\n"
                             f"Вы <b>подтверждаете</b> этот адрес?", reply_markup=reply_approve_kb)
        await state.update_data(address=address, latitude=location.latitude, longitude=location.longitude)
        await Order.ApproveLocation.set()
        return

    flag = await user_functions.check_user_addresses(session, cust_telegram_id=message.from_user.id)

    if message.text == "⬅️ Назад":
        if flag:
            await message.answer("📍 Отправьте геопозицию или выберите адрес из сохранённых:",
                                 reply_markup=delivery_location_kb(has_addresses=flag))
        else:
            await message.answer("📍 Отправьте геопозицию:", reply_markup=delivery_location_kb(has_addresses=flag))
        return

    if not flag:
        await message.answer("📍 Отправьте геопозицию:", reply_markup=delivery_location_kb(has_addresses=flag))
        return

    addresses = await user_functions.get_user_addresses(session, cust_telegram_id=message.from_user.id)
    if message.text not in addresses:
        await message.answer("Выберите адрес из представленных ниже:",
                             reply_markup=saved_locations_kb(addresses=addresses))
        return

    address_obj = await user_functions.get_user_address_obj(session, cust_telegram_id=message.from_user.id,
                                                            address=message.text)

    await message.answer(f"📍 Адрес, по которому будет доставлен заказ: <b>{message.text}</b>.\n"
                         f"Вы <b>подтверждаете</b> этот адрес?", reply_markup=reply_approve_kb)
    await state.update_data(address=message.text, latitude=address_obj.latitude, longitude=address_obj.longitude)
    await Order.ApproveLocation.set()


@rate_limit(1)
async def approve_delivery_location(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == "✅ Да":

        async with state.proxy() as data:
            latitude = data.get("latitude")
            longitude = data.get("longitude")
        delivery_cost = calc_delivery_cost(cust_latitude=latitude, cust_longitude=longitude, km_price=KM_DELIVERY_PRICE)

        # Точка входа в меню кафе
        top_msg = await message.answer("Выберите категорию: (Тут уже будет меню...)", reply_markup=reply_cancel_kb)
        await state.update_data(delivery_cost=delivery_cost, top_msg_id=top_msg.message_id, selected_products={})
        await list_categories(message, state, session)
        await Order.Menu.set()

    elif message.text == "❌ Нет":
        flag = await user_functions.check_user_addresses(session, cust_telegram_id=message.from_user.id)
        if flag:
            await message.answer("📍 Отправьте геопозицию или выберите адрес из сохранённых:",
                                 reply_markup=delivery_location_kb(has_addresses=flag))
        else:
            await message.answer("📍 Отправьте геопозицию:", reply_markup=delivery_location_kb(has_addresses=flag))
        await Order.GetLocation.set()
    else:
        await message.answer("Некорректный ввод. Используйте кнопки ниже:", reply_markup=reply_approve_kb)
        await Order.ApproveLocation.set()


@rate_limit(1)
async def cancel_order(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        top_msg_id = data.get("top_msg_id")
        menu_msg_id = data.get("menu_msg_id")
        ph_msg_id = data.get("ph_msg_id")

    try:
        if top_msg_id:
            await message.bot.delete_message(chat_id=message.from_user.id, message_id=top_msg_id)
        if ph_msg_id:
            await message.bot.delete_message(chat_id=message.from_user.id, message_id=ph_msg_id)
        if menu_msg_id:
            await message.bot.delete_message(chat_id=message.from_user.id, message_id=menu_msg_id)
    except MessageToDeleteNotFound as error:
        logging.error(error)
        pass

    await state.reset_data()
    await state.reset_state()
    await message.answer("😔 Заказ отменён.", reply_markup=main_menu_kb)


def register_order(dp: Dispatcher):
    dp.register_message_handler(cancel_order, text="❌ Отмена",
                                state=[Order.GetOrderType, Order.GetLocation, Order.ApproveLocation, Order.Menu])
    dp.register_message_handler(get_order_type, content_types=types.ContentType.TEXT, state=Order.GetOrderType)
    dp.register_message_handler(choose_saved_delivery_location, text="🗺 Мои адреса", state=Order.GetLocation)
    dp.register_message_handler(get_delivery_location, content_types=[types.ContentType.LOCATION,
                                                                      types.ContentType.TEXT], state=Order.GetLocation)
    dp.register_message_handler(approve_delivery_location, content_types=types.ContentType.TEXT,
                                state=Order.ApproveLocation)
