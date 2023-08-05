from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncResult, AsyncSession
from sqlalchemy.dialects.postgresql import insert

from tgbot.infrastructure.database.db_models.settings_model import ServiceNote


async def add_service_note(session: object, name: str, value_1: int = None,
                           value_2: int = None, value_3: float = None, value_4: float = None,
                           value_5: str = None, value_6: str = None) -> object:
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
            value_4=value_4,
            value_5=value_5,
            value_6=value_6
        ).returning(ServiceNote).on_conflict_do_nothing()
    )
    result = await session.scalars(insert_stmt)
    return result.first()


async def update_active_users_count(session: AsyncSession, count: int):
    stmt = update(ServiceNote).where(ServiceNote.name == "active_users").values(
        value_1=count
    )
    await session.execute(stmt)


async def get_active_users_count(session: AsyncSession):
    stmt = select(ServiceNote).where(ServiceNote.name == "active_users")
    result: AsyncResult = await session.scalars(stmt)
    service_note = result.unique().first()
    return service_note.value_1


async def update_tou_file_id(session: AsyncSession, file_id: str):
    stmt = update(ServiceNote).where(ServiceNote.name == "terms_of_use").values(
        value_5=file_id
    )
    await session.execute(stmt)


async def select_tou_file_id(session):
    stmt = select(ServiceNote).where(ServiceNote.name == "terms_of_use")
    result: AsyncResult = await session.scalars(stmt)
    service_note = result.unique().first()
    return service_note.value_5
