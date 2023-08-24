from sqlalchemy import Column, VARCHAR, BIGINT, Integer, FLOAT
from tgbot.infrastructure.database.db_models.base_model import TimeStampMixin, DatabaseModel


class User(DatabaseModel, TimeStampMixin):
    telegram_id = Column(BIGINT, nullable=False, autoincrement=False, primary_key=True)
    full_name = Column(VARCHAR(100), nullable=False)
    phone_number = Column(VARCHAR(25), nullable=True)

    role = Column(VARCHAR(10), nullable=False)


class Address(DatabaseModel):
    address_id = Column(VARCHAR(20), nullable=False, autoincrement=False, primary_key=True)
    cust_telegram_id = Column(BIGINT, nullable=False, autoincrement=False)
    latitude = Column(FLOAT, nullable=False)
    longitude = Column(FLOAT, nullable=False)
    address = Column(VARCHAR(200), nullable=False)


class Feedback(DatabaseModel):
    feedback_id = Column(VARCHAR(15), primary_key=True)
    cust_telegram_id = Column(BIGINT, nullable=False, autoincrement=False)
    feedback_text = Column(VARCHAR(450), nullable=False)


class BlockedUser(DatabaseModel, TimeStampMixin):
    """
    Global block in bot
    """

    blocked_user_id = Column(BIGINT, nullable=False, autoincrement=False, primary_key=True)
    blocked_by_moderator_id = Column(BIGINT, nullable=False, autoincrement=False)

    block_reason = Column(VARCHAR(500), nullable=False, default="Отсутствует")
