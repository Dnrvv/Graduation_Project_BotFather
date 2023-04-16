import logging

from aiogram import Bot

from tgbot.infrastructure.database.db_functions.user_functions import get_user, add_user
from tgbot.misc.constants import Roles


async def assign_admin_roles(session, bot: Bot, admins: list[int]):
    for admin_id in admins:
        db_user = await get_user(session, telegram_id=admin_id)
        logging.info(f"Assigning admin role to {db_user}: {admins}")
        if not db_user:
            try:
                admin_user = await bot.get_chat(admin_id)
            except Exception as e:
                logging.error(f'Error while getting admin user: {e}')
                continue

            await add_user(
                session,
                admin_user.id, admin_user.full_name, Roles.ADMIN
            )
            await session.commit()
            # await bot.send_message(chat_id=admin_id, text="You're now an admin!")
