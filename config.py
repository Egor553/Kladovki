import os
import random
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Инициализация логгера
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8116404876:AAHWPmfrDN5pWSq6kHCDFsrGIByWfNttpdQ")
ADMIN_CHAT_ID = os.getenv(
    "ADMIN_CHAT_ID", "-1003458828164"
)  # ID чата для получения заявок


def load_proxies(file_path: str = "proxies.txt") -> list:
    """Загрузка прокси из файла"""
    proxies = []
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        proxies.append(line)
        if not proxies:
            logger.warning(
                f"Файл {file_path} пуст или не найден. Прокси не будут использоваться."
            )
    except Exception as e:
        logger.error(f"Ошибка при загрузке прокси: {e}")
    return proxies


def get_random_proxy() -> Optional[str]:
    """Получить случайный прокси"""
    proxies = load_proxies()
    if proxies:
        return random.choice(proxies)
    return None


# Варианты площади
AREA_OPTIONS = {
    "4": {
        "name": "4 м²",
        "dimensions": "1.5 м длина / 2.5 м ширина / 2.6 м высота",
        "price_from": "от 1000 ₽/месяц",
    },
    "8": {
        "name": "8 м²",
        "dimensions": "3.2 м / 2.5 м / 2.6 м высота",
        "price_from": "от 2000 ₽/месяц",
    },
    "15": {
        "name": "15 м²",
        "dimensions": "6 м / 2.5 м / 2.6 м высота",
        "price_from": "от 7000 ₽/месяц",
    },
    "30": {
        "name": "30 м²",
        "dimensions": "12 м / 2.5 м / 2.6 м высота",
        "price_from": "от 10500 ₽/месяц",
    },
}

# Локации с координатами для карт
# Координаты: latitude, longitude
LOCATIONS = [
    {
        "id": "1",
        "name": "Ижевская, 108",
        "address": "Челябинск, ул. Ижевская, 108",
        "latitude": 55.1800,
        "longitude": 61.4000,
        "schedule": "24/7",
        "is_promotion": False,
        "has_forklift": False,
    },
    {
        "id": "2",
        "name": "Генерала Мартынова, 20",
        "address": "Челябинск, ул. Генерала Мартынова, 20",
        "latitude": 55.1700,
        "longitude": 61.4100,
        "schedule": "с 8.00 до 22.00",
        "is_promotion": False,
        "has_forklift": False,
    },
    {
        "id": "3",
        "name": "Пр-т Ленина, 2А",
        "address": "Челябинск, пр-т Ленина, 2А",
        "latitude": 55.1600,
        "longitude": 61.4300,
        "schedule": "24/7",
        "is_promotion": True,
        "has_forklift": True,
    },
    {
        "id": "4",
        "name": "Кожзаводская, 20",
        "address": "Челябинск, ул. Кожзаводская, 20",
        "latitude": 55.1500,
        "longitude": 61.4200,
        "schedule": "24/7",
        "is_promotion": False,
        "has_forklift": False,
    },
    {
        "id": "5",
        "name": "Харлова, 5А",
        "address": "Челябинск, ул. Харлова, 5А",
        "latitude": 55.1400,
        "longitude": 61.4400,
        "schedule": "с 8.00 до 21.00",
        "is_promotion": False,
        "has_forklift": False,
    },
    {
        "id": "6",
        "name": "Блюхера, 62",
        "address": "Челябинск, ул. Блюхера, 62",
        "latitude": 55.1300,
        "longitude": 61.4500,
        "schedule": "с 8.00 до 22.00",
        "is_promotion": False,
        "has_forklift": False,
    },
    {
        "id": "7",
        "name": "Свердловский тракт, 38",
        "address": "Челябинск, Свердловский тракт, 38",
        "latitude": 55.1200,
        "longitude": 61.4600,
        "schedule": "с 7.00 до 20.00",
        "is_promotion": True,
        "has_forklift": False,
    },
    {
        "id": "8",
        "name": "Сетевая, 5/6",
        "address": "Челябинск, ул. Сетевая, 5/6",
        "latitude": 55.1100,
        "longitude": 61.4700,
        "schedule": "24/7",
        "is_promotion": False,
        "has_forklift": False,
    },
    {
        "id": "9",
        "name": "Новоградская, 1а",
        "address": "Челябинск, ул. Новоградская, 1а",
        "latitude": 55.1000,
        "longitude": 61.4800,
        "schedule": "24/7",
        "is_promotion": True,
        "has_forklift": True,
    },
    {
        "id": "10",
        "name": "Заболотная, 18/3",
        "address": "Челябинск, ул. Заболотная, 18/3",
        "latitude": 55.0900,
        "longitude": 61.4900,
        "schedule": "24/7",
        "is_promotion": True,
        "has_forklift": True,
    },
    {
        "id": "11",
        "name": "ВГ Костицына, 7",
        "address": "Челябинск, ВГ Костицына, 7",
        "latitude": 55.0800,
        "longitude": 61.5000,
        "schedule": "24/7",
        "is_promotion": False,
        "has_forklift": False,
    },
    {
        "id": "12",
        "name": "Ул. Солнечная, 6В",
        "address": "Челябинск, ул. Солнечная, 6В",
        "latitude": 55.0700,
        "longitude": 61.5100,
        "schedule": "24/7",
        "is_promotion": False,
        "has_forklift": False,
    },
    {
        "id": "13",
        "name": "Ул. Университетская Набережная, 66В",
        "address": "Челябинск, ул. Университетская Набережная, 66В",
        "latitude": 55.0600,
        "longitude": 61.5200,
        "schedule": "с 8.00 до 21.00",
        "is_promotion": True,
        "has_forklift": False,
    },
    {
        "id": "14",
        "name": "Хохрякова, 31",
        "address": "Челябинск, ул. Хохрякова, 31",
        "latitude": 55.0500,
        "longitude": 61.5300,
        "schedule": "24/7",
        "is_promotion": False,
        "has_forklift": False,
    },
    {
        "id": "15",
        "name": "Копейск, 1ый Снайперский пер., 16",
        "address": "Копейск, 1ый Снайперский пер., 16",
        "latitude": 54.9000,
        "longitude": 61.6000,
        "schedule": "с 7.00 до 22.00",
        "is_promotion": True,
        "has_forklift": False,
    },
]

# Контакт для газели и грузчиков
LOADERS_CONTACT = "Дмитрий +79227004908"


def get_map_link(address: str) -> str:
    """Генерация ссылки на Яндекс.Карты"""
    from urllib.parse import quote

    return f"https://yandex.ru/maps/?text={quote(address)}"


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Расчет расстояния между двумя точками по формуле гаверсинуса (в км)"""
    from math import radians, sin, cos, sqrt, atan2

    R = 6371  # Радиус Земли в км
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def find_nearest_locations(user_lat: float, user_lon: float, limit: int = 5) -> list:
    """Найти ближайшие локации к пользователю"""
    locations_with_distance = []

    for location in LOCATIONS:
        if "latitude" in location and "longitude" in location:
            distance = calculate_distance(
                user_lat, user_lon, location["latitude"], location["longitude"]
            )
            locations_with_distance.append({**location, "distance": distance})

    # Сортируем по расстоянию
    locations_with_distance.sort(key=lambda x: x["distance"])

    return locations_with_distance[:limit]


# Инициализация логгера для config
import logging

logger = logging.getLogger(__name__)
