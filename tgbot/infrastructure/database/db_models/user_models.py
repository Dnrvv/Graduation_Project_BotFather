from sqlalchemy import Column, VARCHAR, BIGINT
from tgbot.infrastructure.database.db_models.base_model import TimeStampMixin, DatabaseModel


class User(DatabaseModel, TimeStampMixin):
    telegram_id = Column(BIGINT, nullable=False, autoincrement=False, primary_key=True)

    role = Column(VARCHAR(10), nullable=False)


class BlockedUser(DatabaseModel, TimeStampMixin):
    """
    Global block in bot
    """

    blocked_user_id = Column(BIGINT, nullable=False, autoincrement=False, primary_key=True)
    blocked_by_moderator_id = Column(BIGINT, nullable=False, autoincrement=False)

    block_reason = Column(VARCHAR(500), nullable=False, default="Отсутствует")
