from aiogram import types
from aiogram.types import BotCommand

from tgbot.config import Config


async def set_bot_commands(dp, config: Config):
    default_commands = {
        "menu": "Главное меню",
        "start": "Перезапустить бота",
        "help": "Помощь"
    }

    admin_commands = {
        "statistics": "Статистика бота",
        "notify_users": "Уведомить пользователей",
        "menu": "Главное меню",
        "start": "Перезапустить бота",
        "help": "Помощь"
    }

    await dp.bot.set_my_commands(
        [BotCommand(name, value) for name, value in default_commands.items()],
        scope=types.BotCommandScopeDefault()
    )

    await dp.bot.set_my_commands(
        [BotCommand(name, value) for name, value in admin_commands.items()],
        scope=types.BotCommandScopeChat(chat_id=config.tg_bot.admin_ids[0]))
