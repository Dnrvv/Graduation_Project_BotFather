from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.infrastructure.database.db_functions import order_functions, product_functions
from tgbot.services.service_functions import format_number_with_spaces, number_to_emoji, calc_delivery_time


async def create_cart_text(selected_products: dict, delivery_cost: int, session: AsyncSession):
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
    return cart_text, total_products_cost


async def create_order_checkout_text(address: str, phone_number: str, selected_products: dict,
                                     total_products_cost: int, delivery_cost: int, is_approved: bool,
                                     session: AsyncSession, order_id: int = None, latitude: float = None,
                                     longitude: float = None) -> str:

    if is_approved:
        order_checkout_text = (f"Номер заказа: <b>{order_id}</b>\n"
                               f"Адрес: {address}\n\n")
    else:
        order_checkout_text = (f"<b>Ваш заказ:</b>\n"
                               f"Адрес: {address}\n"
                               f"Номер телефона: {phone_number}\n\n")

    for product_id, quantity in selected_products.items():
        product_obj = await product_functions.get_product(session, product_id=int(product_id))
        cart_product_cost = quantity * product_obj.product_price

        order_checkout_text += f"<b>{product_obj.product_name}</b>\n"
        order_checkout_text += (f"<b> {number_to_emoji(quantity)}</b> ✖️ "
                                f"{format_number_with_spaces(product_obj.product_price)} "
                                f"= {format_number_with_spaces(cart_product_cost)} сум \n")
        if is_approved:
            await order_functions.add_order_product(session, order_id=order_id,
                                                    product_id=product_obj.product_id,
                                                    product_quantity=quantity)

    if is_approved:
        order_checkout_text += (f"\n<b>Продукты:</b> {format_number_with_spaces(total_products_cost)} сум\n"
                                f"<b>Доставка:</b> {format_number_with_spaces(delivery_cost)} сум\n"
                                f"<b>Итого: {format_number_with_spaces(total_products_cost + delivery_cost)} сум</b>\n\n"
                                f"<b>Ваш заказ оформлен.</b>\n"
                                f"Время доставки ~ <b>{calc_delivery_time(latitude, longitude)}</b> минут.")
    else:
        order_checkout_text += (f"\n<b>Продукты:</b> {format_number_with_spaces(total_products_cost)} сум\n"
                                f"<b>Доставка:</b> {format_number_with_spaces(delivery_cost)} сум\n"
                                f"<b>Итого: {format_number_with_spaces(total_products_cost + delivery_cost)} сум</b>\n\n"
                                f"<b>Подтвердить заказ?</b>")

    return order_checkout_text


async def create_order_history_text(order_obj, session: AsyncSession):
    delivery_obj = await order_functions.get_delivery_obj(session, order_id=order_obj.order_id)
    order_products = await order_functions.get_user_order_products(session, order_id=order_obj.order_id)

    address_obj = await order_functions.get_delivery_address(session, order_id=order_obj.order_id)

    text = (f"Номер заказа: <b>{order_obj.order_id}</b>\n"
            f"Дата заказа: <b>{order_obj.created_at.strftime('%d-%m-%Y %H:%M')}</b>\n"
            f"Адрес: {address_obj.address}\n\n")
    total_products_cost = 0
    print(order_products)
    for order_product in order_products:
        product_obj = await product_functions.get_product(session, product_id=order_product.product_id)

        cart_product_cost = order_product.product_quantity * product_obj.product_price
        total_products_cost += cart_product_cost

        text += f"<b>{product_obj.product_name}</b>\n"
        text += (f"<b> {number_to_emoji(order_product.product_quantity)}</b> ✖️ "
                 f"{format_number_with_spaces(product_obj.product_price)} "
                 f"= {format_number_with_spaces(cart_product_cost)} сум \n")

    text += (f"\n<b>Продукты:</b> {format_number_with_spaces(total_products_cost)} сум\n"
             f"<b>Доставка:</b> {format_number_with_spaces(delivery_obj.delivery_cost)} сум\n"
             f"<b>Итого: {format_number_with_spaces(total_products_cost + delivery_obj.delivery_cost)} сум</b>")
    return text


async def create_edited_product_text(product_id: int, session: AsyncSession, product_name: str = None,
                                     product_caption: str = None, product_price: int = None):
    old_product_obj = await product_functions.get_product(session, product_id=product_id)
    text = ""
    if product_name:
        text += (f"Название: <b>{product_name}</b>\n\n"
                 f"Описание: {old_product_obj.product_caption}\n\n"
                 f"Цена: {format_number_with_spaces(old_product_obj.product_price)} сум\n\n")
    elif product_caption:
        text += (f"Название: <b>{old_product_obj.product_name}</b>\n\n"
                 f"Описание: {product_caption}\n\n"
                 f"Цена: {format_number_with_spaces(old_product_obj.product_price)} сум\n\n")
    elif product_price:
        text += (f"Название: <b>{old_product_obj.product_name}</b>\n\n"
                 f"Описание: {old_product_obj.product_caption}\n\n"
                 f"Цена: {format_number_with_spaces(product_price)} сум\n\n")
    else:
        text += (f"Название: <b>{old_product_obj.product_name}</b>\n\n"
                 f"Описание: {old_product_obj.product_caption}\n\n"
                 f"Цена: {format_number_with_spaces(old_product_obj.product_price)} сум\n\n")
    return text
