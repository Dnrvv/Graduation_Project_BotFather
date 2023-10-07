from aiogram import types
from aiogram.types import BotCommand

from tgbot.config import Config


async def set_bot_commands(dp, config: Config):
    default_commands = {
        "start": "Перезапустить бота",
        "order": "Сделать заказ",
        "my_balance": "Мой баланс",
        "my_referer_link": "Ссылка для приглашения"
    }

    admin_commands = {
        "start": "Перезапустить бота",
        "notify_users": "Уведомить пользователей",
        "statistics": "Статистика бота",
        "moderation_menu": "Меню модерации",
        "my_balance": "Мой баланс",
        "my_referer_link": "Ссылка для приглашения"
    }

    await dp.bot.set_my_commands(
        [BotCommand(name, value) for name, value in default_commands.items()],
        scope=types.BotCommandScopeDefault()
    )

    await dp.bot.set_my_commands(
        [BotCommand(name, value) for name, value in admin_commands.items()],
        scope=types.BotCommandScopeChat(chat_id=config.tg_bot.admin_ids[0]))
