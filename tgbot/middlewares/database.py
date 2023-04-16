from typing import Dict, Any

from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from aiogram.types import CallbackQuery, Message
from aiogram.types.base import TelegramObject

from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.infrastructure.database.db_functions import user_functions
from tgbot.infrastructure.database.db_functions.user_functions import get_user


class DatabaseMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["update"]

    def __init__(self, session_pool):
        super().__init__()
        self.__session_pool = session_pool

    async def pre_process(self, obj: [CallbackQuery, Message], data: Dict, *args: Any) -> None:
        session: AsyncSession = self.__session_pool()
        data["session"] = session
        data["session_pool"] = self.__session_pool
        if not getattr(obj, "from_user", None):
            return

        if obj.from_user:
            user = await get_user(session, telegram_id=obj.from_user.id)

            if not user:
                await user_functions.add_user(session, telegram_id=obj.from_user.id)

            data['user'] = user

    async def post_process(self, obj: TelegramObject, data: Dict, *args: Any) -> None:
        if session := data.get("session", None):
            session: AsyncSession
            await session.close()
