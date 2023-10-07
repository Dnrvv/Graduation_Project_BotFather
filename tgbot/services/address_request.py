
import asyncio
import concurrent.futures
import requests

from tgbot.misc.dependences import ALLOWED_CITIES


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


NOMINATIM_URL = 'https://nominatim.openstreetmap.org/reverse'


async def get_address(lat, lon):
    url = f'{NOMINATIM_URL}?lat={lat}&lon={lon}&format=json&accept-language=ru'
    response = await get(url)
    if response.status_code == 200:
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
    else:
        return None
