from typing import Callable, AsyncContextManager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from tgbot.config import DbConfig
from tgbot.infrastructure.database.db_models.base_model import DatabaseModel, Base


async def create_session_pool(db: DbConfig, drop_tables: bool = False,
                              echo=False) -> Callable[[], AsyncContextManager[AsyncSession]]:

    engine = create_async_engine(
        db.construct_sqlalchemy_url(),
        query_cache_size=1200,
        pool_size=10,
        max_overflow=200,
        future=True,
        echo=echo,
    )

    async with engine.begin() as conn:
        if drop_tables:
            await conn.run_sync(DatabaseModel.metadata.drop_all)
        await conn.run_sync(DatabaseModel.metadata.create_all)

    session_pool = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

    return session_pool

