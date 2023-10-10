import logging

from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.infrastructure.database.db_functions import currency_functions
from tgbot.infrastructure.database.db_models.currency_model import Currency
from tgbot.misc.dependences import CURRENCIES
from tgbot.services.request_functions import get_currency_exchange_rate


async def add_currencies(session: AsyncSession):
    for currency in CURRENCIES:
        await currency_functions.add_currency(session, currency_code=currency)


async def update_currencies(session: AsyncSession):
    for currency in CURRENCIES:
        course_to_uzs = await get_currency_exchange_rate(source_currency=currency, target_currency="UZS")
        if course_to_uzs == 0:
            logging.info(f"No correct value in API JSON.")
            continue
        elif course_to_uzs == -1:
            logging.info(f"response code != 200 or there is no quotes in API JSON.")
            continue
        elif course_to_uzs == -2:
            logging.info("Critical error in API response.")
            continue

        await currency_functions.update_currency(session, Currency.currency_code == currency,
                                                 course_to_uzs=course_to_uzs)
        logging.info(f"Successfully updated {currency} course_to_uzs value.")
    await session.commit()
