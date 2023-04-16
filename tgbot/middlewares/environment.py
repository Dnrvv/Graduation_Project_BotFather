from typing import Dict, Any

from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from aiogram.types import CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler


class EnvironmentMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    def __init__(self, scheduler: AsyncIOScheduler, **kwargs):
        super().__init__()
        self._scheduler = scheduler
        self.kwargs = kwargs

    async def pre_process(self, obj: [CallbackQuery, Message], data: Dict, *args: Any) -> None:
        data["scheduler"] = self._scheduler
        data.update(**self.kwargs)
