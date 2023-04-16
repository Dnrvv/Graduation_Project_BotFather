from typing import Dict, Any

from aiogram import Dispatcher
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from aiogram.types import ReplyKeyboardRemove, CallbackQuery, Message
from aiogram.types.base import TelegramObject
from aiogram.utils.markdown import quote_html
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.infrastructure.database.db_functions.user_functions import get_user
from tgbot.misc.dependences import BLOCKED_IDS, BLOCKED_USER_FULLNAMES
from tgbot.misc.states import Auth


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

        if obj.from_user.id in BLOCKED_IDS or obj.from_user.full_name in BLOCKED_USER_FULLNAMES:
            raise CancelHandler()

        if obj.from_user:
            user = await get_user(session, telegram_id=obj.from_user.id)

            if not user:
                dispatcher = Dispatcher.get_current()
                state = dispatcher.current_state()
                state_name = await state.get_state()
                bot = dispatcher.bot
                if state_name == "Auth:PasswordConfirm":
                    return
                else:
                    await bot.send_message(text=f"👾 Здравствуйте, {quote_html(obj.from_user.full_name)}! "
                                                f"Введите пароль:",
                                           reply_markup=ReplyKeyboardRemove(), chat_id=obj.from_user.id)
                    await Auth.PasswordConfirm.set()
                    raise CancelHandler()

            data['user'] = user

    async def post_process(self, obj: TelegramObject, data: Dict, *args: Any) -> None:
        if session := data.get("session", None):
            session: AsyncSession
            await session.close()
