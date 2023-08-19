from sqlalchemy import Column, VARCHAR, BIGINT, Integer, FLOAT
from tgbot.infrastructure.database.db_models.base_model import TimeStampMixin, DatabaseModel


class Order(DatabaseModel, TimeStampMixin):
    order_id = Column(VARCHAR(50), nullable=False, autoincrement=False, primary_key=True)
    cust_telegram_id = Column(BIGINT, nullable=False, autoincrement=False)
    order_type = Column(VARCHAR(20), nullable=False)
    payment_type = Column(VARCHAR(20), nullable=False, default="cash")
    order_status = Column(VARCHAR(20), nullable=False)


class OrderProduct(DatabaseModel):
    order_prod_id = Column(BIGINT, autoincrement=True, primary_key=True)
    order_id = Column(VARCHAR(50), nullable=False, autoincrement=False)
    product_id = Column(VARCHAR(50), nullable=False)


class Product(DatabaseModel):
    product_id = Column(VARCHAR(20), nullable=False, primary_key=True)
    photo_file_id = Column(VARCHAR(150), nullable=False)

    category_code = Column(VARCHAR(20))
    category_name = Column(VARCHAR(25))

    subcategory_code = Column(VARCHAR(20))
    subcategory_name = Column(VARCHAR(25))

    product_name = Column(VARCHAR(150), nullable=False)
    product_caption = Column(VARCHAR(250), nullable=False)
    product_price = Column(FLOAT, nullable=False, default=0)


class Delivery(DatabaseModel):
    delivery_id = Column(VARCHAR(50), nullable=False, autoincrement=False, primary_key=True)
    delivery_address_id = Column(VARCHAR(50), nullable=False, autoincrement=False)
    order_id = Column(VARCHAR(50), nullable=False, autoincrement=False)
    courier_name = Column(VARCHAR(100), nullable=False)
    courier_phone = Column(VARCHAR(25), nullable=False)
    delivery_price = Column(FLOAT, nullable=False, default=0)


