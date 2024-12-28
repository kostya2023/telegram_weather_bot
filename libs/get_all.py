import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()
token = os.getenv("Dadata_token")
openkey = os.getenv("openWeatherMap")


if token is None:
    raise ValueError("Токен Dadata не найден. Убедитесь, что он указан в .env файле.")


def get_city(lat: float, lon: float):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Token " + token
    }

    data = {
        "lat": lat,
        "lon": lon,
        "count": 1,
        "radius_meters": 1000,
        "language": "ru"
    }

    try:
        response = requests.post("http://suggestions.dadata.ru/suggestions/api/4_1/rs/geolocate/address", 
                                 json=data, headers=headers)

        response.raise_for_status()
        response_data = response.json()

        if response_data.get("suggestions"):
            city_name = response_data['suggestions'][0]['data']['city']
            return city_name
        else:
            return "Город не найден."

    except requests.exceptions.RequestException as e:
        return f"Ошибка при выполнении запроса: {e}"

def get_weather(city):
    print(city)

    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={openkey}&units=metric'
    response = requests.get(url)
    data = response.text
    data = json.loads(data)
    print("Main:", data["main"])
    print("wind:", data["wind"])
    print("visibility:", data["visibility"])
    print(data)
    return [data["main"], data["wind"], data["visibility"]]


# print("Определение города...")
# city = get_city(56.115596, 47.451418)
# print(f"Определено. Город: {city}")
# print("Определяем погоду...")
# print("Погода:")
# print(get_weather(city))