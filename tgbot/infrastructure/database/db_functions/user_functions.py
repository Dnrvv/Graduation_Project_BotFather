from sqlalchemy import select, update, func, and_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncResult, AsyncSession

from tgbot.infrastructure.database.db_models.order_models import Order
from tgbot.infrastructure.database.db_models.user_models import User, Address
from tgbot.services.service_functions import generate_random_id


async def add_user(session: AsyncSession, telegram_id: int, full_name: str, role='user'):
    insert_stmt = select(
        User
    ).from_statement(
        insert(
            User
        ).values(
            telegram_id=telegram_id,
            full_name=full_name,
            role=role
        ).returning(User).on_conflict_do_nothing()
    )
    result = await session.scalars(insert_stmt)
    return result.first()


async def add_user_address(session: AsyncSession, cust_telegram_id: int, latitude: float, longitude: float,
                           address: str):
    insert_stmt = select(
        Address
    ).from_statement(
        insert(
            Address
        ).values(
            address_id=generate_random_id(20),
            cust_telegram_id=cust_telegram_id,
            latitude=latitude,
            longitude=longitude,
            address=address
        ).returning(Address).on_conflict_do_nothing()
    )

    result = await session.scalars(insert_stmt)
    return result.first()


async def get_user_address_obj(session: AsyncSession, cust_telegram_id: int, address: str):
    stmt = select(Address).where(and_(Address.cust_telegram_id == cust_telegram_id,
                                      Address.address == address))
    result: AsyncResult = await session.scalars(stmt)
    return result.first()


async def check_user_addresses(session: AsyncSession, cust_telegram_id: int) -> bool:
    stmt = select(func.count(Address.address)).where(Address.cust_telegram_id == cust_telegram_id)
    result: AsyncResult = await session.scalar(stmt)
    return result > 0


async def get_user_addresses(session: AsyncSession, cust_telegram_id: int):
    stmt = select(Address.address).where(Address.cust_telegram_id == cust_telegram_id)
    result: AsyncResult = await session.scalars(stmt)
    return result.unique().all()


async def get_user(session: AsyncSession, telegram_id: int) -> User:
    stmt = select(User).where(User.telegram_id == telegram_id)
    result: AsyncResult = await session.scalars(stmt)
    return result.first()


async def get_user_phone_number(session: AsyncSession, order_id: int):
    stmt = select(Order).where(Order.order_id == order_id)
    order = await session.scalar(stmt)
    if order:
        user_obj = await get_user(session, telegram_id=order.cust_telegram_id)
        return user_obj.phone_number
    return None


async def get_some_users(session: AsyncSession, *clauses) -> list[User]:
    stmt = select(User).where(*clauses).order_by(User.created_at.desc())
    result: AsyncResult = await session.scalars(stmt)
    return result.unique().all()


async def get_users_count(session: AsyncSession, *clauses) -> int:
    stmt = select(func.count(User.telegram_id)).where(*clauses)
    result: AsyncResult = await session.scalar(stmt)
    return result


async def update_user(session: AsyncSession, *clauses, **values):
    stmt = update(User).where(*clauses).values(**values)
    await session.execute(stmt)
