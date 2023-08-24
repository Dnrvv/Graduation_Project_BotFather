from sqlalchemy import select, update, func, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncResult, AsyncSession

from tgbot.infrastructure.database.db_models.order_models import Order, OrderProduct, Product, Delivery
from tgbot.infrastructure.database.db_models.user_models import Address
from tgbot.services.service_functions import generate_random_id


async def add_order(session: AsyncSession, cust_telegram_id: int, order_type: str, payment_type: str,
                    order_status: str):
    insert_stmt = select(
        Order
    ).from_statement(
        insert(
            Order
        ).values(
            cust_telegram_id=cust_telegram_id,
            order_type=order_type,
            payment_type=payment_type,
            order_status=order_status
        ).returning(Order).on_conflict_do_nothing()
    )
    result = await session.scalars(insert_stmt)
    return result.first()


async def add_order_product(session: AsyncSession, order_id: str, product_id: str, product_quantity: int):
    insert_stmt = select(
        OrderProduct
    ).from_statement(
        insert(
            OrderProduct
        ).values(
            order_prod_id=generate_random_id(20),
            order_id=order_id,
            product_id=product_id,
            product_quantity=product_quantity
        ).returning(OrderProduct).on_conflict_do_nothing()
    )
    result = await session.scalars(insert_stmt)
    return result.first()


async def add_delivery(session: AsyncSession, delivery_address_id: str, order_id: int, delivery_cost: int,
                       courier_name: str = None, courier_phone: str = None, ):
    insert_stmt = select(
        Delivery
    ).from_statement(
        insert(
            Delivery
        ).values(
            delivery_id=generate_random_id(20),
            delivery_address_id=delivery_address_id,
            order_id=order_id,
            courier_name=courier_name,
            courier_phone=courier_phone,
            delivery_cost=delivery_cost
        ).returning(Delivery).on_conflict_do_nothing()
    )
    result = await session.scalars(insert_stmt)
    return result.first()


async def get_user_orders_count(session: AsyncSession, cust_telegram_id: int):
    stmt = select(func.count(Order.cust_telegram_id)).where(Order.cust_telegram_id == cust_telegram_id)
    result: AsyncResult = await session.scalar(stmt)
    return result


async def get_user_order_pagination(session: AsyncSession, cust_telegram_id: int, counter: int):
    stmt = (
        select(Order)
        .where(Order.cust_telegram_id == cust_telegram_id)
        .order_by(Order.created_at)
    )

    result: AsyncResult = await session.execute(stmt)
    orders = result.scalars().all()

    if counter <= len(orders):
        return orders[counter - 1]

    return None


async def get_user_order_products(session: AsyncSession, order_id: int):
    stmt = select(OrderProduct).where(OrderProduct.order_id == order_id)
    result: AsyncResult = await session.scalars(stmt)
    return result.unique().all()


async def get_delivery_obj(session: AsyncSession, order_id: int):
    stmt = select(Delivery).where(Delivery.order_id == order_id)
    result: AsyncResult = await session.scalars(stmt)
    return result.first()


async def get_delivery_address(session: AsyncSession, order_id: int):
    stmt = select(Delivery).where(Delivery.order_id == order_id)
    delivery = await session.scalar(stmt)
    if delivery:
        address_id = delivery.delivery_address_id
        address = await session.get(Address, address_id)
        return address
    return None


async def get_orders_count(session: AsyncSession) -> int:
    stmt = select(func.count(Order.order_id))
    result: AsyncResult = await session.scalar(stmt)
    return result
