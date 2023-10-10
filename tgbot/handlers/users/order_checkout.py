import logging
import re

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageToDeleteNotFound
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.config import load_config
from tgbot.infrastructure.database.db_functions import order_functions, user_functions
from tgbot.infrastructure.database.db_models.user_models import User
from tgbot.keyboards.menu_inline_kbs import categories_keyboard, cart_actions_cd
from tgbot.keyboards.reply_kbs import get_contact_kb, order_approve_kb, main_menu_kb, reply_cancel_kb
from tgbot.middlewares.throttling import rate_limit
from tgbot.misc.states import Order

from tgbot.services.text_formatting_functions import create_order_checkout_text


@rate_limit(1)
async def cart_actions(call: types.CallbackQuery, callback_data: dict, state: FSMContext,
                       session: AsyncSession):

    action = callback_data.get("action")
    if action == "order_checkout":
        async with state.proxy() as data:
            total_products_cost = int(data.get("total_products_cost"))
            delivery_cost = int(data.get("delivery_cost"))

        user = await user_functions.get_user(session, telegram_id=call.from_user.id)
        if user.balance < total_products_cost + delivery_cost:
            await call.answer("😭 На Вашем балансе недостаточно средств.", show_alert=True)
            return

        await call.answer()
        await call.message.edit_reply_markup()

        text = "Отправьте или введите ваш номер телефона в формате: <b>+998 ** *** ** **</b>"

        phone_request_msg = await call.message.answer(text=text, reply_markup=get_contact_kb)
        await state.update_data(phone_request_msg_id=phone_request_msg.message_id)
        await Order.GetContact.set()
        return
    elif action == "clear_cart":
        await call.answer()
        async with state.proxy() as data:
            data["selected_products"] = {}

        await call.message.edit_text("🧹 Корзина очищена")
        keyboard = await categories_keyboard(session=session)
        menu_msg = await call.message.answer("🍴 Выберите категорию:", reply_markup=keyboard)
        await state.update_data(ph_msg_id=None, menu_msg_id=menu_msg.message_id, quantity_counter=1)


@rate_limit(1)
async def get_contact(message: types.Message, state: FSMContext, session: AsyncSession):
    phone_number = ""
    if message.contact:
        phone_number = message.contact.phone_number
        if "+" not in phone_number:
            phone_number = f"+{phone_number}"
        await state.update_data(phone_number=phone_number)

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

    else:
        pattern = r'^\+? ?998 ?\d{2} ?\d{3} ?\d{2} ?\d{2}$'
        match = re.match(pattern, message.text)
        if match:
            phone_number = message.text.replace(" ", "")
            await state.update_data(phone_number=phone_number)
        else:
            await message.answer("Пожалуйста, следуйте формату: <b>+998 ** *** ** **</b>")

    # тут нужно уже вывести заказ для подтверждения пользователем
    async with state.proxy() as data:
        delivery_cost = data.get("delivery_cost")
        address = data.get("address")
        selected_products = data.get("selected_products", {})
        total_products_cost = data.get("total_products_cost")

    order_checkout_text = await create_order_checkout_text(address=address, phone_number=phone_number,
                                                           selected_products=selected_products,
                                                           total_products_cost=total_products_cost,
                                                           delivery_cost=delivery_cost,
                                                           session=session, is_approved=False)

    await message.answer(text=order_checkout_text)
    await Order.OrderApprove.set()


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

        # -------------------- Обращение к базе данных ------------------------
        order_obj = await order_functions.add_order(session, cust_telegram_id=message.from_user.id,
                                                    order_type=order_type, order_status="Новый")

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

        await user_functions.update_user(session, User.telegram_id == message.from_user.id, phone_number=phone_number)
        user_obj = await user_functions.get_user(session, telegram_id=message.from_user.id)
        await user_functions.update_user(session, User.telegram_id == message.from_user.id,
                                         balance=user_obj.balance - (total_products_cost + delivery_cost))

        # --------------------------------------------------------------------

        order_checkout_text = await create_order_checkout_text(address=address, phone_number=phone_number,
                                                               selected_products=selected_products,
                                                               total_products_cost=total_products_cost,
                                                               delivery_cost=delivery_cost,
                                                               session=session, is_approved=True,
                                                               order_id=order_obj.order_id,
                                                               latitude=latitude, longitude=longitude)
        await session.commit()

        await message.answer(text=order_checkout_text, reply_markup=main_menu_kb)

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
    dp.register_message_handler(approve_order, content_types=types.ContentType.TEXT, state=Order.OrderApprove)
