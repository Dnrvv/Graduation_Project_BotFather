from sqlalchemy import Column, VARCHAR, BIGINT, Integer, FLOAT, BOOLEAN
from tgbot.infrastructure.database.db_models.base_model import TimeStampMixin, DatabaseModel


class Order(DatabaseModel, TimeStampMixin):
    order_id = Column(BIGINT, nullable=False, autoincrement=True, primary_key=True)
    cust_telegram_id = Column(BIGINT, nullable=False, autoincrement=False)
    order_type = Column(VARCHAR(20), nullable=False)
    order_status = Column(VARCHAR(20), nullable=False, default="Новый")


class OrderProduct(DatabaseModel):
    order_prod_id = Column(VARCHAR(20), primary_key=True)
    order_id = Column(BIGINT, nullable=False)
    product_id = Column(Integer, nullable=False)
    product_quantity = Column(Integer, nullable=False, default=1)


class Product(DatabaseModel):
    product_id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    photo_file_id = Column(VARCHAR(150), nullable=False)
    photo_web_link = Column(VARCHAR(500), nullable=False)

    category_code = Column(VARCHAR(20))
    category_name = Column(VARCHAR(25))

    product_name = Column(VARCHAR(150), nullable=False, unique=True)
    product_caption = Column(VARCHAR(250), nullable=False)
    product_price = Column(Integer, nullable=False, default=0)

    is_hidden = Column(BOOLEAN, nullable=False, default=False)


class Delivery(DatabaseModel):
    delivery_id = Column(VARCHAR(20), nullable=False, autoincrement=False, primary_key=True)
    delivery_address_id = Column(VARCHAR(30), nullable=False, autoincrement=False)
    order_id = Column(BIGINT, nullable=False)
    delivery_cost = Column(Integer, nullable=False, default=0)
    courier_name = Column(VARCHAR(100), nullable=True)
    courier_phone = Column(VARCHAR(25), nullable=True)
