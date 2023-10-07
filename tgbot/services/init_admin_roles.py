import logging

from aiogram import Bot

from tgbot.infrastructure.database.db_functions.user_functions import get_user, add_user, update_user
from tgbot.infrastructure.database.db_models.user_models import User


async def assign_service_roles(session, bot: Bot, admins: list[int], operators: list[int]):
    for admin_id in admins:
        db_user = await get_user(session, telegram_id=admin_id)
        logging.info(f"Assigning admin role to {db_user}: {admins}")
        if not db_user:
            try:
                admin_user = await bot.get_chat(admin_id)
            except Exception as e:
                logging.error(f'Error while getting admin user: {e}')
                continue

            await add_user(session, admin_user.id, full_name="ADMIN", role="Admin")
            await update_user(session, User.telegram_id == admin_user.id, balance=100000)
            await session.commit()
            await bot.send_message(chat_id=admin_id, text="👮‍♂️ Вам выданы права <b>администратора</b>.")

    for operator_id in operators:
        db_user = await get_user(session, telegram_id=operator_id)
        logging.info(f"Assigning admin role to {db_user}: {admins}")
        if not db_user:
            try:
                admin_user = await bot.get_chat(operator_id)
            except Exception as e:
                logging.error(f'Error while getting operator user: {e}')
                continue

            await add_user(session, admin_user.id, full_name="OPERATOR", role="Operator")
            await session.commit()
            await bot.send_message(chat_id=operator_id, text="👮‍♂️ Вам выданы права <b>оператора</b>.")
