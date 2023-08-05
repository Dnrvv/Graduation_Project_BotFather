import typing

from aiogram.dispatcher.filters import BoundFilter

from tgbot.config import Config


class AdminFilter(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin: typing.Optional[bool] = None):
        self.is_admin = is_admin

    async def check(self, obj):
        if self.is_admin is None:
            return False
        config: Config = obj.bot.get('config')
        return (obj.from_user.id in config.tg_bot.admin_ids) == self.is_admin


class ModeratorFilter(BoundFilter):
    key = 'is_moderator'

    def __init__(self, is_moderator: typing.Optional[bool] = None):
        self.is_moderator = is_moderator

    async def check(self, obj):
        if self.is_moderator is None:
            return False
        config: Config = obj.bot.get('config')
        return (obj.from_user.id in config.tg_bot.moderator_ids) == self.is_moderator


class OperatorFilter(BoundFilter):
    key = 'is_operator'

    def __init__(self, is_operator: typing.Optional[bool] = None):
        self.is_operator = is_operator

    async def check(self, obj):
        if self.is_operator is None:
            return False
        config: Config = obj.bot.get('config')
        return (obj.from_user.id in config.tg_bot.operator_ids) == self.is_operator


class SpectatorFilter(BoundFilter):
    key = 'is_spectator'

    def __init__(self, is_spectator: typing.Optional[bool] = None):
        self.is_spectator = is_spectator

    async def check(self, obj):
        if self.is_spectator is None:
            return False
        config: Config = obj.bot.get('config')
        return (obj.from_user.id in config.tg_bot.spectator_ids) == self.is_spectator
