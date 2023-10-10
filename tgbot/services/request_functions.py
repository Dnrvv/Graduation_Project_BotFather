import asyncio
import concurrent.futures
import logging

import requests

from tgbot.config import load_config
from tgbot.misc.dependences import ALLOWED_CITIES


async def run_blocking_io(func, *args):
    """
    Description: This asynchronous function is a utility function used to run a given function with its arguments
    in a separate thread, allowing non-blocking execution of blocking I/O operations. It uses the ThreadPoolExecutor
    to run the specified function in a separate thread and returns the result.
    Parameters:
    func: The function to be executed in a separate thread.
    *args: Variable-length positional arguments to be passed to the function.
    Returns: An awaitable object representing the result of executing the specified function with the given arguments
    in a separate thread.
    """
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, func, *args)
    return result


async def get(url):
    """
    Description: This asynchronous function performs an HTTP GET request to the specified URL using the
    requests.get method. It does so in a non-blocking manner using the run_blocking_io function to execute the
    request in a separate thread.
    Parameters:
    url (str): The URL to which the GET request should be made.
    Returns: An awaitable object representing the response from the GET request.
    """
    return await run_blocking_io(requests.get, url)


async def get_address(lat: float, lon: float):
    url = f'https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=ru'
    response = await get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    city = data.get('address', {}).get('city', 'Unknown City')
    street = data.get('address', {}).get('road', 'Unknown Street')
    house_number = data.get('address', {}).get('house_number', '')

    if city not in ALLOWED_CITIES:
        return "Incorrect city"

    if "Unknown" in street:
        street = "Неизвестная улица"
    else:
        street = street.replace(" улица", "")

    full_address = f"{city}, ул. {street}"

    if house_number:
        full_address += f", {house_number}"

    return full_address


async def get_currency_exchange_rate(source_currency: str = "USD", target_currency: str = "UZS"):
    api_key = load_config().tg_bot.currency_api_key

    url = f"https://api.apilayer.com/currency_data/live?source={source_currency}&" \
          f"currencies={target_currency}&apikey={api_key}"

    try:
        response = await get(url)
        data = response.json()
        if response.status_code != 200 or "quotes" not in data:
            return -1

        exchange_rate = data["quotes"].get(f"{source_currency}{target_currency}")

        if not exchange_rate:
            return 0

        # print(f"Курс {source_currency} к {target_currency}: {exchange_rate}")
        return exchange_rate

    except Exception as e:
        logging.info(e)
        # print(f"Произошла ошибка: {str(e)}")
        return -2
