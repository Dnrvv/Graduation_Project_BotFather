import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from tgbot.config import load_config, Config
from tgbot.filters.admin import AdminFilter
from tgbot.handlers.echo import register_echo
from tgbot.handlers.errors_handler import register_errors_handler
from tgbot.handlers.users.additional_commands import register_additional_commands
from tgbot.handlers.users.bot_start import register_bot_start
from tgbot.handlers.users.notify_users import register_notify_users

from tgbot.infrastructure.database.db_functions.setup_functions import create_session_pool
from tgbot.middlewares.database import DatabaseMiddleware
from tgbot.middlewares.environment import EnvironmentMiddleware
from tgbot.middlewares.throttling import ThrottlingMiddleware
from tgbot.services.broadcast_functions import broadcast
from tgbot.services.init_admin_roles import assign_admin_roles
from tgbot.services.set_bot_commands import set_bot_commands

logger = logging.getLogger(__name__)


def register_all_middlewares(dp, session_pool, scheduler, environment: dict):
    dp.setup_middleware(ThrottlingMiddleware())
    dp.setup_middleware(DatabaseMiddleware(session_pool))
    dp.setup_middleware(EnvironmentMiddleware(scheduler, **environment))


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp):
    register_bot_start(dp)

    register_errors_handler(dp)

    register_additional_commands(dp)
    register_notify_users(dp)

    register_echo(dp)


async def on_startup(session_pool, bot: Bot, config: Config):
    logger.info("Bot started")
    session: AsyncSession = session_pool()

    await assign_admin_roles(session, bot, config.tg_bot.admin_ids)
    notify_text = "👨‍💻 Сообщение для администрации:\n<b>Бот запущен!</b> /start"
    await broadcast(bot, config.tg_bot.admin_ids, notify_text)

    await session.close()


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config(".env")

    storage = RedisStorage2(host='redis') if config.tg_bot.use_redis else MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)
    scheduler = AsyncIOScheduler()
    bot['config'] = config

    session_pool = await create_session_pool(config.db, drop_tables=True, echo=True)

    register_all_middlewares(
        dp,
        session_pool=session_pool,
        scheduler=scheduler,
        environment=dict(config=config)
    )

    register_all_filters(dp)
    register_all_handlers(dp)

    await set_bot_commands(dp, config=config)
    await on_startup(session_pool, bot, config)

    try:
        # scheduler.start()   !!!
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
