from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, AsyncResult

from tgbot.infrastructure.database.db_models.feedback_model import Feedback


async def add_feedback(session: AsyncSession, cust_telegram_id: int, feedback_text: str):
    insert_stmt = select(
        Feedback
    ).from_statement(
        insert(
            Feedback
        ).values(
            cust_telegram_id=cust_telegram_id,
            feedback_text=feedback_text
        ).returning(Feedback).on_conflict_do_nothing()
    )
    result = await session.scalars(insert_stmt)
    return result.first()


async def get_feedback(session: AsyncSession, feedback_num: int):
    stmt = select(Feedback).where(Feedback.feedback_num == feedback_num)
    result: AsyncResult = await session.scalars(stmt)
    return result.first()


async def get_feedbacks_count(session: AsyncSession) -> int:
    stmt = select(func.count(Feedback.feedback_num))
    result: AsyncResult = await session.scalar(stmt)
    return result

