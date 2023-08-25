from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.infrastructure.database.db_functions import order_functions, product_functions
from tgbot.services.service_functions import format_number_with_spaces, number_to_emoji


async def parse_user_order_text(order_obj, session: AsyncSession):
    delivery_obj = await order_functions.get_delivery_obj(session, order_id=order_obj.order_id)
    order_products = await order_functions.get_user_order_products(session, order_id=order_obj.order_id)

    address_obj = await order_functions.get_delivery_address(session, order_id=order_obj.order_id)
    text = (f"Номер заказа: <b>{order_obj.order_id}</b>\n"
            f"Дата заказа: {order_obj.created_at.strftime('%d-%m-%Y %H:%M')}\n"
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

    text += (f"\nТип оплаты: {order_obj.payment_type}\n"
             f"\n<b>Продукты:</b> {format_number_with_spaces(total_products_cost)} сум\n"
             f"<b>Доставка:</b> {format_number_with_spaces(delivery_obj.delivery_cost)} сум\n"
             f"<b>Итого: {format_number_with_spaces(total_products_cost + delivery_obj.delivery_cost)} сум</b>")
    return text
