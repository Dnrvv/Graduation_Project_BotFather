import logging
import re

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageToDeleteNotFound
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.infrastructure.database.db_functions import product_functions, order_functions, user_functions
from tgbot.keyboards.generate_keyboards import categories_keyboard, cart_actions_cd
from tgbot.keyboards.reply_kbs import get_contact_kb, payment_type_kb, order_approve_kb, main_menu_kb, reply_cancel_kb
from tgbot.middlewares.throttling import rate_limit
from tgbot.misc.states import Order
from tgbot.services.service_functions import number_to_emoji, format_number_with_spaces, calc_delivery_time


@rate_limit(1)
async def cart_actions(call: types.CallbackQuery, callback_data: dict, state: FSMContext,
                       session: AsyncSession):
    await call.answer()
    action = callback_data.get("action")
    if action == "order_checkout":
        await call.message.edit_reply_markup()
        text = ("Отправьте или введите ваш номер телефона в формате: <b>+998 ** *** ** **</b>\n\n" 
                "<i><b>Примечание:</b> если Вы планируете оплатить заказ онлайн с помощью Click или Payme, то "
                "пожалуйста, укажите номер телефона, на который зарегистрирован аккаунт в соответствующем сервисе.</i>")
        phone_request_msg = await call.message.answer(text=text, reply_markup=get_contact_kb)
        await state.update_data(phone_request_msg_id=phone_request_msg.message_id)
        await Order.GetContact.set()
        return
    elif action == "clear_cart":
        async with state.proxy() as data:
            data["selected_products"] = {}
        await call.message.edit_text("🧹 Корзина очищена")
        keyboard = await categories_keyboard(session=session)
        menu_msg = await call.message.answer("🍴 Выберите категорию:", reply_markup=keyboard)
        await state.update_data(ph_msg_id=None, menu_msg_id=menu_msg.message_id, quantity_counter=1)
    elif action == "set_delivery_time":
        await call.answer("Пока что в разработке")


@rate_limit(1)
async def get_contact(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.contact:
        phone_number = message.contact.phone_number
        if "+" not in phone_number:
            phone_number = f"+{phone_number}"
        await state.update_data(phone_number=phone_number)
        await message.answer("💸 Выберите тип оплаты:", reply_markup=payment_type_kb)
        await Order.GetPaymentType.set()
        return
    elif message.text == "⬅️ Назад":
        async with state.proxy() as data:
            top_msg_id = data.get("top_msg_id")
            phone_request_msg_id = data.get("phone_request_msg_id")

        try:
            if top_msg_id:
                await message.bot.delete_message(chat_id=message.from_user.id, message_id=top_msg_id)
            if phone_request_msg_id:
                await message.bot.delete_message(chat_id=message.from_user.id, message_id=phone_request_msg_id)
        except MessageToDeleteNotFound as error:
            logging.error(error)
            pass

        keyboard = await categories_keyboard(session=session)
        top_msg = await message.answer("Выберите категорию: (Тут уже будет меню...)", reply_markup=reply_cancel_kb)
        menu_msg = await message.answer("🍴 Выберите категорию:", reply_markup=keyboard)
        await state.update_data(top_msg_id=top_msg.message_id, menu_msg_id=menu_msg.message_id)
        await Order.Menu.set()
        return

    pattern = r'^\+998 ?\d{2} ?\d{3} ?\d{2} ?\d{2}$'
    match = re.match(pattern, message.text)
    if match:
        phone_number = message.text.replace(" ", "")
        await state.update_data(phone_number=phone_number)
        await message.answer("💸 Выберите тип оплаты:", reply_markup=payment_type_kb)
        await Order.GetPaymentType.set()
    else:
        await message.answer("Пожалуйста, следуйте формату: <b>+998 ** *** ** **</b>")


@rate_limit(1)
async def get_payment_type(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text not in ["Наличные", "Click", "Payme"]:
        await message.answer("Некорректный ввод. Используйте кнопки ниже:", reply_markup=payment_type_kb)
        return

    await state.update_data(payment_type=message.text)

    async with state.proxy() as data:
        delivery_cost = data.get("delivery_cost")
        address = data.get("address")
        phone_number = data.get("phone_number")
        selected_products = data.get("selected_products", {})
        total_products_cost = data.get("total_products_cost")

    order_checkout_text = (f"<b>Ваш заказ:</b>\n"
                           f"Адрес: {address}\n"
                           f"Номер телефона: {phone_number}\n\n")

    for product_id, quantity in selected_products.items():
        product_obj = await product_functions.get_product(session, product_id=product_id)
        cart_product_cost = quantity * product_obj.product_price

        order_checkout_text += f"<b>{product_obj.product_name}</b>\n"
        order_checkout_text += (f"<b> {number_to_emoji(quantity)}</b> ✖️ "
                                f"{format_number_with_spaces(product_obj.product_price)} "
                                f"= {format_number_with_spaces(cart_product_cost)} сум \n")

    order_checkout_text += (f"\nТип оплаты: {message.text}\n"
                            f"\n<b>Продукты:</b> {format_number_with_spaces(total_products_cost)} сум\n"
                            f"<b>Доставка:</b> {format_number_with_spaces(delivery_cost)} сум\n"
                            f"<b>Итого: {format_number_with_spaces(total_products_cost + delivery_cost)} сум</b>\n\n"
                            f"<b>Подтвердить заказ?</b>")

    await message.answer(text=order_checkout_text, reply_markup=order_approve_kb)
    await Order.ApproveOrder.set()


@rate_limit(1)
async def approve_order(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == "✅ Подтвердить":
        async with state.proxy() as data:
            order_type = data.get("order_type")
            delivery_cost = data.get("delivery_cost")
            latitude = float(data.get("latitude"))
            longitude = float(data.get("longitude"))
            address = data.get("address")
            phone_number = data.get("phone_number")
            selected_products = data.get("selected_products", {})
            total_products_cost = data.get("total_products_cost")
            payment_type = data.get("payment_type")

        # -------------------- Обращение к базе данных ------------------------
        order_obj = await order_functions.add_order(session, cust_telegram_id=message.from_user.id,
                                                    order_type=order_type, payment_type=payment_type,
                                                    order_status="Новый")

        customer_addresses = await user_functions.get_user_addresses(session, cust_telegram_id=message.from_user.id)
        if address not in customer_addresses:
            address_obj = await user_functions.add_user_address(session, cust_telegram_id=message.from_user.id,
                                                                address=address, latitude=latitude, longitude=longitude)
        else:
            address_obj = await user_functions.get_user_address_obj(session, cust_telegram_id=message.from_user.id,
                                                                    address=address)
        address_id = address_obj.address_id

        await order_functions.add_delivery(session, delivery_address_id=address_id, order_id=order_obj.order_id,
                                           delivery_cost=delivery_cost)

        await user_functions.update_user_phone(session, telegram_id=message.from_user.id, phone_number=phone_number)

        # ---------------------------------------------------------

        order_info_text = (f"Номер заказа: <b>{order_obj.order_id}</b>\n"
                           f"Адрес: {address}\n\n")

        for product_id, quantity in selected_products.items():
            product_obj = await product_functions.get_product(session, product_id=product_id)
            order_info_text += f"<b>{product_obj.product_name}</b>\n"
            cart_product_cost = quantity * product_obj.product_price
            order_info_text += (f"<b> {number_to_emoji(quantity)}</b> ✖️ "
                                f"{format_number_with_spaces(product_obj.product_price)} "
                                f"= {format_number_with_spaces(cart_product_cost)} сум \n")
            await order_functions.add_order_product(session, order_id=order_obj.order_id,
                                                    product_id=product_obj.product_id,
                                                    product_quantity=quantity)

        await session.commit()

        order_info_text += (f"\nТип оплаты: {payment_type}\n"
                            f"\n<b>Продукты:</b> {format_number_with_spaces(total_products_cost)} сум\n"
                            f"<b>Доставка:</b> {format_number_with_spaces(delivery_cost)} сум\n"
                            f"<b>Итого: {format_number_with_spaces(total_products_cost + delivery_cost)} сум</b>\n\n"
                            f"<b>Ваш заказ оформлен.</b>\n"
                            f"Время доставки - <b>{calc_delivery_time(latitude, longitude)}</b> минут.")

        await message.answer(text=order_info_text, reply_markup=main_menu_kb)

    elif message.text == "❌ Отменить":
        await message.answer("😔 Заказ отменён.", reply_markup=main_menu_kb)

    else:
        await message.answer("Некорректный ввод. Используйте кнопки ниже:", reply_markup=order_approve_kb)
        return

    await state.reset_data()
    await state.finish()


def register_order_checkout(dp: Dispatcher):
    dp.register_callback_query_handler(cart_actions, cart_actions_cd.filter(), state=Order.Menu)
    dp.register_message_handler(get_contact, content_types=[types.ContentType.TEXT, types.ContentType.CONTACT],
                                state=Order.GetContact)
    dp.register_message_handler(get_payment_type, content_types=types.ContentType.TEXT, state=Order.GetPaymentType)
    dp.register_message_handler(approve_order, content_types=types.ContentType.TEXT, state=Order.ApproveOrder)
