import math
import random
import string

from tgbot.cafe_branches import Branches


def generate_random_id(length: int):
    """
    Generates random combination of symbols for questionnaire_id in database
    """

    symbols = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(symbols) for i in range(length))


URL = "http://maps.google.com/maps?q={lat},{lon}"
R = 6378.1


def show_on_gmaps(lat, lon):
    return URL.format(lat=lat, lon=lon)


def calc_distance(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    # Radius of earth in kilometers is 6371
    km = 6371 * c
    return math.ceil(km)


def choose_shortest(cust_latitude: float, cust_longitude: float):
    # distances = list()
    distances = {}

    for cafe_name, cafe_location in Branches:
        distance = calc_distance(cust_latitude, cust_longitude,
                                 cafe_location["lat"], cafe_location["lon"])
        distances[cafe_name] = distance

    sorted_distances = dict(sorted(distances.items(), key=lambda x: x[1]))
    return sorted_distances

    # for cafe_name, cafe_location in Branches:
    #     distances.append((cafe_name,
    #                       calc_distance(cust_latitude, cust_longitude,
    #                                     cafe_location["lat"], cafe_location["lon"]),
    #                       show_on_gmaps(**cafe_location),
    #                       cafe_location
    #                       ))
    # return sorted(distances, key=lambda x: x[1])[:1]  # Последняя 1 - означает выдать только 1 филиал


def calc_delivery_cost(cust_latitude: float, cust_longitude: float, km_price: int):
    nearest_branch = choose_shortest(cust_latitude, cust_longitude)
    return int(round(next(iter(nearest_branch.values())) * km_price, -3))


def calc_delivery_time(cust_latitude: float, cust_longitude: float):
    distance = calc_distance(cust_latitude, cust_longitude, 41.31066997, 69.28147451)
    # тут какие-то расчеты
    return 30


def number_to_emoji(number):
    if 1 <= number <= 100:
        emojis = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
        number_str = str(number)
        emoji_str = ''.join(emojis[int(digit)] for digit in number_str)
        return emoji_str


def format_number_with_spaces(number):
    formatted_number = "{:,}".format(number).replace(',', ' ')
    return formatted_number
