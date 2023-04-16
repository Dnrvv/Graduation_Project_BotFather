import asyncio
import typing

from aiogram import Dispatcher, types
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled


class ThrottlingMiddleware(BaseMiddleware):
    """
    Simple middleware
    """

    def __init__(self, limit=DEFAULT_RATE_LIMIT, key_prefix="antiflood_"):
        self.rate_limit = limit
        self.prefix = key_prefix
        self.service_text = ('❗️ <b>Пожалуйста, не используйте команды слишком часто!</b>\n'
                             '🔓 Доступ к боту будет возобновлён через <b>5</b> секунд...')
        super(ThrottlingMiddleware, self).__init__()

    # noinspection PyUnusedLocal
    async def on_process_message(self, message: types.Message, data: dict):
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()
        if handler:
            limit = getattr(handler, 'throttling_rate_limit', self.rate_limit)
            key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"
        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            await self.message_throttled(message, t)
            raise CancelHandler()

    async def message_throttled(self, message: types.Message, throttled: Throttled):
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()
        if handler:
            key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
            text = getattr(handler, "throttling_text", self.service_text)
        else:
            text = self.service_text
            key = f"{self.prefix}_message"
        delta = throttled.rate - throttled.delta

        if throttled.exceeded_count <= 2:
            service_message = await message.reply(text)

            await asyncio.sleep(5)
            await service_message.delete()
            await message.delete()
        try:
            await message.delete()
        except Exception as err:
            print(err)
            pass


def rate_limit(limit: int, key=None, text: typing.Optional[str] = None):
    """
    Decorator for configuring rate limit and key in different functions.
    :param limit:
    :param key:
    :param text:
    :return:
    """
    def decorator(func):
        setattr(func, "throttling_rate_limit", limit)
        if key:
            setattr(func, "throttling_key", key)
        if text:
            setattr(func, "throttling_text", text)

        return func
    return decorator