from aiogram import types
from aiogram.types import BotCommand

from tgbot.config import Config


async def set_bot_commands(dp, config: Config):
    default_commands = {
        "start": "Перезапустить бота",
        "order": "Сделать заказ",
    }

    admin_commands = {
        "start": "Перезапустить бота",
        "order": "Сделать заказ",
        "notify_users": "Уведомить пользователей",
        "statistics": "Статистика бота",
        "moderation_menu": "Меню модерации"
    }

    # moderator_commands = {
    #     "menu": "Главное меню",
    #     "start": "Перезапустить бота",
    #     "help": "Помощь",
    #     "terms_of_use": "Пользовательское соглашение",
    #     "statistics": "Статистика бота",
    #     "get_problematic_users": "Список проблематичных пользователей",
    #     "block_user": "Заблокировать пользователя",
    #     "unblock_user": "Разблокировать пользователя"
    # }

    # spectator_commands = {
    #     "menu": "Главное меню",
    #     "start": "Перезапустить бота",
    #     "help": "Помощь",
    #     "terms_of_use": "Пользовательское соглашение",
    #     "statistics": "Статистика бота",
    # }

    await dp.bot.set_my_commands(
        [BotCommand(name, value) for name, value in default_commands.items()],
        scope=types.BotCommandScopeDefault()
    )

    await dp.bot.set_my_commands(
        [BotCommand(name, value) for name, value in admin_commands.items()],
        scope=types.BotCommandScopeChat(chat_id=config.tg_bot.admin_ids[0]))

    # for moderator_id in config.tg_bot.moderator_ids:
    #     await dp.bot.set_my_commands(
    #         [BotCommand(name, value) for name, value in moderator_commands.items()],
    #         scope=types.BotCommandScopeChat(chat_id=moderator_id))
    #
    # for spectator_id in config.tg_bot.spectator_ids:
    #     await dp.bot.set_my_commands(
    #         [BotCommand(name, value) for name, value in spectator_commands.items()],
    #         scope=types.BotCommandScopeChat(chat_id=spectator_id))