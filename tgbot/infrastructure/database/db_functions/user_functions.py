from sqlalchemy import select, update, func, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncResult, AsyncSession

from tgbot.infrastructure.database.db_models.user_models import User, BlockedUser


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


async def block_user(session: AsyncSession, blocked_user_id: int, blocked_by_moderator_id: int,
                     block_reason: str = None):
    insert_stmt = select(
        BlockedUser
    ).from_statement(
        insert(
            BlockedUser
        ).values(
            blocked_user_id=blocked_user_id,
            blocked_by_moderator_id=blocked_by_moderator_id,
            block_reason=block_reason
        ).returning(BlockedUser).on_conflict_do_nothing()
    )
    result = await session.scalars(insert_stmt)
    return result.first()


async def unblock_user(session: AsyncSession, blocked_user_id: int):
    stmt = delete(BlockedUser).where(BlockedUser.blocked_user_id == blocked_user_id)
    await session.execute(stmt)


async def get_blocked_user(session: AsyncSession, blocked_user_id: int):
    stmt = select(BlockedUser).where(BlockedUser.blocked_user_id == blocked_user_id)
    result: AsyncResult = await session.scalars(stmt)
    return result.first()


async def get_user(session: AsyncSession, telegram_id: int) -> User:
    stmt = select(User).where(User.telegram_id == telegram_id)
    result: AsyncResult = await session.scalars(stmt)
    return result.first()


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

