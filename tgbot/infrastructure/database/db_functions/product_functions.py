from sqlalchemy import select, update, func, delete, and_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncResult, AsyncSession

from tgbot.infrastructure.database.db_models.order_models import Product
from tgbot.services.service_functions import generate_random_id


async def add_product(session: AsyncSession, photo_file_id: str, category_code: str, category_name: str,
                      product_name: str, product_caption: str,
                      product_price: int):
    insert_stmt = select(
        Product
    ).from_statement(
        insert(
            Product
        ).values(
            product_id=generate_random_id(10),
            photo_file_id=photo_file_id,
            category_code=category_code,
            category_name=category_name,
            product_name=product_name,
            product_caption=product_caption,
            product_price=product_price
        ).returning(Product).on_conflict_do_nothing()
    )
    result = await session.scalars(insert_stmt)
    return result.first()


async def get_categories(session: AsyncSession):
    stmt = (
        select(Product.category_code, Product.category_name)
        .distinct()
        .group_by(Product.category_code, Product.category_name)
    )

    result: AsyncResult = await session.execute(stmt)
    categories = result.all()

    category_dict = {category.category_code: category.category_name for category in categories}
    return category_dict


async def get_products(session: AsyncSession, category_code: str):
    stmt = select(Product).where(Product.category_code == category_code)
    result: AsyncResult = await session.scalars(stmt)
    return result.unique().all()


async def get_product(session: AsyncSession, product_id: str):
    stmt = select(Product).where(Product.product_id == product_id)
    result: AsyncResult = await session.scalars(stmt)
    return result.first()
