
import asyncio
import concurrent.futures
import requests


async def get(url):
    return await run_blocking_io(requests.get, url)


async def run_blocking_io(func, *args):
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
        full_address = ""

        if city != "Ташкент":
            return -1

        if "Unknown" in street:
            street = "Неизвестная улица"
        else:
            street = street.replace(" улица", "")

        if house_number:
            full_address += f", {house_number}"

        full_address = f"{city}, улица {street}"
        return full_address
    else:
        return None
