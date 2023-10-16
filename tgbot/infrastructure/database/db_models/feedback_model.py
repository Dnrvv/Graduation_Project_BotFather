from sqlalchemy import Column, VARCHAR, BIGINT, Integer
from tgbot.infrastructure.database.db_models.base_model import TimeStampMixin, DatabaseModel


class Feedback(DatabaseModel, TimeStampMixin):
    feedback_num = Column(Integer, autoincrement=True, primary_key=True)
    cust_telegram_id = Column(BIGINT, nullable=False, autoincrement=False)
    feedback_text = Column(VARCHAR(600), nullable=False)
