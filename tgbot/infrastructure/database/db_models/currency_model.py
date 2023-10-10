from sqlalchemy import Column, VARCHAR, FLOAT
from tgbot.infrastructure.database.db_models.base_model import DatabaseModel, TimeStampMixin


class Currency(DatabaseModel, TimeStampMixin):
    # sell_value - относительно гос валюты (Узбекский сум)
    currency_code = Column(VARCHAR(10), nullable=False, primary_key=True)
    course_to_uzs = Column(FLOAT, nullable=False, unique=False, autoincrement=False, default=0)
