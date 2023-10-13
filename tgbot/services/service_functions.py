import math
import random
import string
from typing import Union

from aiogram import Bot

from tgbot.cafe_branches import Branches


URL = "http://maps.google.com/maps?q={lat},{lon}"
R = 6378.1


def generate_random_id(length: int) -> str:
    """
    Description: This function generates a random string of symbols, including lowercase letters, uppercase letters,
    and digits. The length of the generated string is specified by the length parameter.
    Parameters:
    length (int): The length of the random string to generate.
    Returns: A randomly generated string of the specified length.
    """

    symbols = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(symbols) for _ in range(length))


def show_on_gmaps(lat, lon) -> str:
    """
    Description: This function takes latitude and longitude coordinates and returns a URL formatted to show
    the location on Google Maps.
    Parameters:
    lat (float): Latitude coordinate of the location.
    lon (float): Longitude coordinate of the location.
    Returns: A string containing a URL for displaying the location on Google Maps.
    """
    return URL.format(lat=lat, lon=lon)


def calc_distance(lat1, lon1, lat2, lon2) -> int:
    """
    Description: This function calculates the distance between two sets of latitude and longitude coordinates using
    the Haversine formula. It converts the coordinates to radians and then calculates the great-circle distance
    between them.
    Parameters:
    lat1 (float): Latitude of the first point.
    lon1 (float): Longitude of the first point.
    lat2 (float): Latitude of the second point.
    lon2 (float): Longitude of the second point.
    Returns: The distance between the two points in kilometers, rounded up to the nearest integer.
    """
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    km = 6371 * c
    return math.ceil(km)


def choose_shortest(cust_latitude: float, cust_longitude: float) -> Union[dict, dict]:
    """
    Description: This function takes customer latitude and longitude coordinates and calculates the distance to all
    branches of a cafe. It returns a dictionary with cafe names as keys and their corresponding distances as values,
    sorted in ascending order of distance.
    Parameters:
    cust_latitude (float): Latitude of the customer's location.
    cust_longitude (float): Longitude of the customer's location.
    Returns: A dictionary with cafe names as keys and distances as values, sorted by distance.
    """
    distances = {}
    for cafe_name, cafe_location in Branches:
        distance = calc_distance(cust_latitude, cust_longitude,
                                 cafe_location["lat"], cafe_location["lon"])
        distances[cafe_name] = distance

    sorted_distances = dict(sorted(distances.items(), key=lambda x: x[1]))
    return sorted_distances


def calc_delivery_cost(cust_latitude: float, cust_longitude: float, km_price: int) -> int:
    """
    Description: This function calculates the delivery cost based on the customer's location and a per-kilometer
    delivery price. It uses the choose_shortest function to find the nearest cafe branch and calculates the delivery
    cost based on the distance to that branch.
    Parameters:
    cust_latitude (float): Latitude of the customer's location.
    cust_longitude (float): Longitude of the customer's location.
    km_price (int): Price per kilometer for delivery.
    Returns: The calculated delivery cost as an integer.
    """
    nearest_branch = choose_shortest(cust_latitude, cust_longitude)
    return int(round(next(iter(nearest_branch.values())) * km_price, -3))


def calc_delivery_time(cust_latitude: float, cust_longitude: float) -> int:
    """
    Description: This function estimates the delivery time to the customer's location. It calculates the distance
    between the customer's location and a fixed destination (or to choosen cafe branch) and then
    performs some calculations to estimate the delivery time.
    Parameters:
    cust_latitude (float): Latitude of the customer's location.
    cust_longitude (float): Longitude of the customer's location.
    Returns: An estimated delivery time in minutes as an integer.
    """
    distance = calc_distance(cust_latitude, cust_longitude, 41.31066997, 69.28147451)
    # тут какие-то расчеты
    return 30


def number_to_emoji(number) -> str:
    """
    Description: This function converts a numeric integer value into a string of emojis representing the digits
    of the number. It supports numbers from 1 to 100.
    Parameters:
    number (int): The integer number to be converted into emojis.
    Returns: A string containing emojis representing the digits of the input number.
    """
    if 1 <= number <= 100:
        emojis = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
        number_str = str(number)
        emoji_str = ''.join(emojis[int(digit)] for digit in number_str)
        return emoji_str


def format_number_with_spaces(number: int) -> str:
    """
    Description: This function formats an integer by adding thousands separators (spaces) to improve readability.
    It checks if the number is less than 1000 and, if not, adds commas as thousands separators.
    Parameters:
    number (int): The integer number to be formatted.
    Returns: A string representing the formatted number.
    """

    if number < 1000:
        return str(number)

    formatted_number = "{:,}".format(number).replace(",", " ")
    return formatted_number


async def is_subscribed(user_id: int, channel: Union[int, str]) -> bool:
    """
    Description: This asynchronous function checks if a user is subscribed to a specified channel. It uses the
    Bot object to query the membership status of the user in the channel.
    Parameters:
    user_id (int): The user's ID whose subscription status is to be checked.
    channel (Union[int, str]): The ID or username of the channel to check membership in.
    Returns: A boolean value indicating whether the user is subscribed to the channel (True) or not (False).
    """
    bot = Bot.get_current()
    member = await bot.get_chat_member(user_id=user_id, chat_id=channel)
    return member.is_chat_member()
