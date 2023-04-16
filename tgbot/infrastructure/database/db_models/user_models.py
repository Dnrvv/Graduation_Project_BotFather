from sqlalchemy import Column, VARCHAR, BIGINT
from tgbot.infrastructure.database.db_models.base_model import TimeStampMixin, DatabaseModel


class User(DatabaseModel, TimeStampMixin):
    telegram_id = Column(BIGINT, nullable=False, autoincrement=False, primary_key=True)

    role = Column(VARCHAR(10), nullable=False)
