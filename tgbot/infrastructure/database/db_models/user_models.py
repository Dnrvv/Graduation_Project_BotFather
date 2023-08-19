from sqlalchemy import Column, VARCHAR, BIGINT, Integer
from tgbot.infrastructure.database.db_models.base_model import TimeStampMixin, DatabaseModel


class User(DatabaseModel, TimeStampMixin):
    telegram_id = Column(BIGINT, nullable=False, autoincrement=False, primary_key=True)
    full_name = Column(VARCHAR(100), nullable=False)
    phone = Column(VARCHAR(25), nullable=True)

    role = Column(VARCHAR(10), nullable=False)


class Address(DatabaseModel):
    address_id = Column(VARCHAR(50), nullable=False, autoincrement=False, primary_key=True)
    cust_telegram_id = Column(BIGINT, nullable=False, autoincrement=False)
    address = Column(VARCHAR(200), nullable=False)


class Review(DatabaseModel):
    review_id = Column(VARCHAR(20), primary_key=True)
    cust_telegram_id = Column(BIGINT, nullable=False, autoincrement=False)
    review_text = Column(VARCHAR(450), nullable=False)


class BlockedUser(DatabaseModel, TimeStampMixin):
    """
    Global block in bot
    """

    blocked_user_id = Column(BIGINT, nullable=False, autoincrement=False, primary_key=True)
    blocked_by_moderator_id = Column(BIGINT, nullable=False, autoincrement=False)

    block_reason = Column(VARCHAR(500), nullable=False, default="Отсутствует")
