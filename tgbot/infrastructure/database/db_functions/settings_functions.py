from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncResult, AsyncSession
from sqlalchemy.dialects.postgresql import insert

from tgbot.infrastructure.database.db_models.settings_model import ServiceNote


async def add_service_note(session, name: str, value_1: int = None,
                           value_2: int = None, value_3: float = None, value_4: float = None):
    insert_stmt = select(
        ServiceNote
    ).from_statement(
        insert(
            ServiceNote
        ).values(
            name=name,
            value_1=value_1,
            value_2=value_2,
            value_3=value_3,
            value_4=value_4
        ).returning(ServiceNote).on_conflict_do_nothing()
    )
    result = await session.scalars(insert_stmt)
    return result.first()


async def active_users_count(session: AsyncSession, count: int):
    stmt = update(ServiceNote).where(ServiceNote.name == "active_users").values(
        value_1=count
    )
    await session.execute(stmt)


async def get_active_users_count(session: AsyncSession):
    stmt = select(ServiceNote).where(ServiceNote.name == "active_users")
    result: AsyncResult = await session.scalars(stmt)
    service_note = result.unique().first()
    return service_note.value_1
