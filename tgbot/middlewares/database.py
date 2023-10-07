import re
from typing import Dict, Any

from aiogram import Bot
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from aiogram.types import CallbackQuery, Message, InlineQuery
from aiogram.types.base import TelegramObject


from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.infrastructure.database.db_functions.user_functions import get_user, add_user
from tgbot.misc.dependences import CHANNEL_USERNAME, WARNING_TEXT
from tgbot.services.broadcast_functions import send_text
from tgbot.services.service_functions import is_subscribed


class DatabaseMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["update"]

    def __init__(self, session_pool):
        super().__init__()
        self.__session_pool = session_pool

    async def pre_process(self, obj: [CallbackQuery, Message, InlineQuery], data: Dict, *args: Any) -> None:
        session: AsyncSession = self.__session_pool()
        data["session"] = session
        data["session_pool"] = self.__session_pool
        if not getattr(obj, "from_user", None):
            return

        bot = Bot.get_current()
        user_obj = await get_user(session, telegram_id=obj.from_user.id)

        if isinstance(obj, Message):
            if not user_obj:
                args = obj.get_args()

                if not args:
                    if not await is_subscribed(user_id=obj.from_user.id, channel=CHANNEL_USERNAME):
                        # Ни пригласительной ссылки, ни подписки
                        await send_text(bot=bot, user_id=obj.from_user.id, text=WARNING_TEXT)
                        raise CancelHandler()
                    # Нет пригласительной ссылки, но подписан на канал
                    await add_user(session, telegram_id=obj.from_user.id, full_name=obj.from_user.full_name,
                                   role="User")
                    await session.commit()
                    return

                if not re.match("\d{9,11}", args):
                    if args == "connect_user":
                        await send_text(bot=bot, user_id=obj.from_user.id, text=WARNING_TEXT)
                        raise CancelHandler()
                    # Пригласительная ссылка некорректна с точки зрения формата
                    await send_text(bot=bot, user_id=obj.from_user.id, text="😔 Ссылка некорректна")
                    raise CancelHandler()

                referer_obj = await get_user(session, telegram_id=int(args))
                if not referer_obj:
                    # Пригласительная ссылка некорректна с точки зрения существования рефера
                    await send_text(bot=bot, user_id=obj.from_user.id, text="😔 Ссылка недействительна.")
                    raise CancelHandler()

                # Если всё хорошо, даём пользователю зарегистрироваться в боте через deeplink_bot_start()

        elif isinstance(obj, CallbackQuery) and not user_obj:
            await send_text(bot=bot, user_id=obj.from_user.id, text=WARNING_TEXT)
            raise CancelHandler()

        elif isinstance(obj, InlineQuery) and not user_obj:
            await obj.answer(results=[],
                             switch_pm_text="Бот недоступен. Подключить бота.",
                             switch_pm_parameter="connect_user",
                             cache_time=5)

    async def post_process(self, obj: TelegramObject, data: Dict, *args: Any) -> None:
        if session := data.get("session", None):
            session: AsyncSession
            await session.close()
