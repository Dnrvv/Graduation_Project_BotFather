from sqlalchemy import Column, Integer, VARCHAR, FLOAT
from tgbot.infrastructure.database.db_models.base_model import DatabaseModel


class ServiceNote(DatabaseModel):
    name = Column(VARCHAR(40), primary_key=True)
    value_1 = Column(Integer, nullable=True)
    value_2 = Column(Integer,  nullable=True)
    value_3 = Column(FLOAT, nullable=True)
    value_4 = Column(FLOAT, nullable=True)
    value_5 = Column(VARCHAR(50), nullable=True)
    value_6 = Column(VARCHAR(150), nullable=True)

