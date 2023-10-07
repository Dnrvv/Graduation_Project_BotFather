from sqlalchemy import select, update, func, delete, and_, or_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncResult, AsyncSession

from tgbot.infrastructure.database.db_models.order_models import Product


async def add_product(session: AsyncSession, photo_file_id: str, photo_web_link: str, category_code: str, category_name: str,
                      product_name: str, product_caption: str, product_price: int):
    insert_stmt = select(
        Product
    ).from_statement(
        insert(
            Product
        ).values(
            photo_file_id=photo_file_id,
            photo_web_link=photo_web_link,
            category_code=category_code,
            category_name=category_name,
            product_name=product_name,
            product_caption=product_caption,
            product_price=product_price
        ).returning(Product).on_conflict_do_nothing()
    )
    result = await session.scalars(insert_stmt)
    return result.first()


async def get_all_categories(session: AsyncSession):
    stmt = (
        select(Product.category_code, Product.category_name)
        .distinct()
        .group_by(Product.category_code, Product.category_name)
    )

    result: AsyncResult = await session.execute(stmt)
    categories = result.all()
    category_dict = {category.category_code: category.category_name for category in categories}
    return category_dict


async def get_categories(session: AsyncSession):
    stmt = (
        select(Product.category_code, Product.category_name)
        .distinct()
        .group_by(Product.category_code, Product.category_name)
    )

    result: AsyncResult = await session.execute(stmt)
    categories = result.all()
    category_dict = {}

    for category in categories:
        category_code = category.category_code
        category_name = category.category_name

        stmt_total = select(func.count().label("total_count")).where(
            Product.category_code == category_code
        )

        total_count = await session.scalar(stmt_total)

        stmt_hidden = select(func.count().label("hidden_count")).where(
            and_(
                Product.category_code == category_code,
                Product.is_hidden is True
            )
        )

        hidden_count = await session.scalar(stmt_hidden)

        if total_count > 0 and hidden_count < total_count:
            category_dict[category_code] = category_name

    return category_dict


async def get_products(session: AsyncSession, category_code: str = None):
    if not category_code:
        stmt = select(Product).order_by(Product.product_name)
        result: AsyncResult = await session.scalars(stmt)
        return result.unique().all()
    stmt = select(Product).where(Product.category_code == category_code)
    result: AsyncResult = await session.scalars(stmt)
    return result.unique().all()


async def get_products_via_query(session: AsyncSession, search_text: str):
    stmt = select(Product).where(or_(Product.product_name.like(f"%{search_text}%")))
    result: AsyncResult = await session.scalars(stmt)
    return result.unique().all()


async def get_product(session: AsyncSession, product_id: int):
    stmt = select(Product).where(Product.product_id == product_id)
    result: AsyncResult = await session.scalars(stmt)
    return result.first()


async def get_product_by_name(session: AsyncSession, product_name: str):
    stmt = select(Product).where(Product.product_name == product_name)
    result: AsyncResult = await session.scalars(stmt)
    return result.first()


# UPDATE FUNCTIONS:

async def update_product(session: AsyncSession, *clauses, **values):
    stmt = update(Product).where(*clauses).values(**values)
    await session.execute(stmt)
