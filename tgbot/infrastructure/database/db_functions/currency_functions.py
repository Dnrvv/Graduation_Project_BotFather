from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, AsyncResult

from tgbot.infrastructure.database.db_models.currency_model import Currency


async def add_currency(session: AsyncSession, currency_code: str):
    insert_stmt = select(
        Currency
    ).from_statement(
        insert(
            Currency
        ).values(
            currency_code=currency_code
        ).returning(Currency).on_conflict_do_nothing()
    )
    result = await session.scalars(insert_stmt)
    return result.first()


async def get_currency(session: AsyncSession, currency_code: str):
    stmt = select(Currency).where(Currency.currency_code == currency_code)
    result: AsyncResult = await session.scalars(stmt)
    return result.first()


async def update_currency(session: AsyncSession, *clauses, **values):
    stmt = update(Currency).where(*clauses).values(**values)
    await session.execute(stmt)
