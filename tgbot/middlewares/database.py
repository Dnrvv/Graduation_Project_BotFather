from typing import Dict, Any

from aiogram import Bot
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from aiogram.types import CallbackQuery, Message
from aiogram.types.base import TelegramObject


from sqlalchemy.ext.asyncio import AsyncSession
from tgbot.infrastructure.database.db_functions.user_functions import get_user
from tgbot.keyboards.reply_kbs import check_subscription_kb
from tgbot.misc.dependences import CHANNEL_USERNAME
from tgbot.services.broadcast_functions import send_text
from tgbot.services.service_functions import is_subscribed


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

        bot = Bot.get_current()

        if obj.get_args():
            try:
                int(obj.get_args())
            except TypeError:
                await send_text(bot=bot, user_id=obj.from_user.id, text="😔 Некорректная ссылка.")
                raise CancelHandler()
            return

        elif obj.from_user:
            user = await get_user(session, telegram_id=obj.from_user.id)
            if not user:
                if not await is_subscribed(user_id=obj.from_user.id, channel=CHANNEL_USERNAME):
                    text = (f"😋 Для доступа к боту Вам необходимо подписаться на канал: <b>{CHANNEL_USERNAME}</b>."
                            f"\n\n<i>После подписки нажмите на кнопку ниже:</i>")
                    await send_text(bot=bot, user_id=obj.from_user.id, text=text, reply_markup=check_subscription_kb)
                    raise CancelHandler()

            data['user'] = user

    async def post_process(self, obj: TelegramObject, data: Dict, *args: Any) -> None:
        if session := data.get("session", None):
            session: AsyncSession
            await session.close()
