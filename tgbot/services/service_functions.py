import math
import random
import string

from aiogram import types

from tgbot.cafe_branches import Cafes


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
    return math.ceil(km * 1000)


def choose_shortest(location: types.Location):
    distances = list()
    for cafe_name, cafe_location in Cafes:
        distances.append((cafe_name,
                          calc_distance(location.latitude, location.longitude,
                                        cafe_location["lat"], cafe_location["lon"]),
                          show_on_gmaps(**cafe_location),
                          cafe_location
                          ))
    return sorted(distances, key=lambda x: x[1])[:2]



