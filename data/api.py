import argparse
import json
import requests
from statistics import mode

team_name = "inside_data"


# Функция для получения ближайшего города по координатам (через Nominatim API)
def get_nearest_city(latitude, longitude):
    url = f"https://nominatim.openstreetmap.org/reverse"
    params = {
        "format": "json",
        "lat": latitude,
        "lon": longitude,
        "zoom": 10,  # Уровень детализации, 10 - это город
        "addressdetails": 1
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            location_data = response.json()
            city = location_data.get("address", {}).get("city", "Неизвестный город")
            if city:
                return city
            else:
                return location_data.get("display_name", "Неизвестный регион")
        else:
            return f"Ошибка при получении города: Код {response.status_code}"
    except Exception as e:
        return f"Ошибка при получении города: {e}"


# Функция для конвертации направления ветра из градусов в название направления
def wind_direction_to_text(degrees):
    if degrees >= 337.5 or degrees < 22.5:
        return "Северный"
    elif 22.5 <= degrees < 67.5:
        return "Северо-восточный"
    elif 67.5 <= degrees < 112.5:
        return "Восточный"
    elif 112.5 <= degrees < 157.5:
        return "Юго-восточный"
    elif 157.5 <= degrees < 202.5:
        return "Южный"
    elif 202.5 <= degrees < 247.5:
        return "Юго-западный"
    elif 247.5 <= degrees < 292.5:
        return "Западный"
    else:
        return "Северо-западный"


# Функция для получения метеоданных
def get_historical_weather(latitude, longitude, date):
    url = "https://archive-api.open-meteo.com/v1/era5"

    # Параметры запроса к Open-Meteo API
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": date,
        "end_date": date,  # Однодневный интервал
        "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum",
        "hourly": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,wind_direction_10m,pressure_msl",
        "timezone": "Europe/Moscow"
    }

    # Отправляем запрос
    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to retrieve data", "status_code": response.status_code}


# Основная функция для обращения к API и получения всех данных
def call_api(lat, lng, date):
    # Получаем метеоданные
    weather_data = get_historical_weather(lat, lng, date)

    # Определение ближайшего города
    nearest_city = get_nearest_city(lat, lng)

    if "error" not in weather_data:
        # Извлекаем суточные данные
        max_temp = weather_data["daily"]["temperature_2m_max"][0]
        min_temp = weather_data["daily"]["temperature_2m_min"][0]
        mean_temp = weather_data["daily"]["temperature_2m_mean"][0]
        precipitation_sum = weather_data["daily"]["precipitation_sum"][0]

        # Извлекаем почасовые данные
        wind_speeds = weather_data["hourly"]["wind_speed_10m"]
        wind_directions = weather_data["hourly"]["wind_direction_10m"]
        pressures = weather_data["hourly"]["pressure_msl"]

        # Рассчитываем максимальную скорость ветра
        max_wind_speed = max(wind_speeds)

        # Определяем доминирующее направление ветра
        dominant_wind_direction = mode(wind_directions)
        wind_direction_text = wind_direction_to_text(dominant_wind_direction)

        # Рассчитываем среднее давление и конвертируем из Па в гПа
        avg_pressure = (sum(pressures) / len(pressures)) / 100  # Конвертируем Па в гПа

        # Создаем словарь с переменными для возврата
        weather_variables = {
            "date": date,
            "temperature_mean": mean_temp,
            "temperature_min": min_temp,
            "temperature_max": max_temp,
            "precipitation_sum": precipitation_sum,
            "wind_speed_max": max_wind_speed,
            "wind_direction_degrees": dominant_wind_direction,
            "wind_direction_text": wind_direction_text,
            "pressure_msl": avg_pressure
        }
        return weather_variables
    else:
        return {"error": weather_data["error"], "status_code": weather_data["status_code"]}


# Функция для сохранения результатов в JSON файл
def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lat", type=float, help="Широта")
    parser.add_argument("--lng", type=float, help="Долгота")
    parser.add_argument("--date", type=str, help="Дата в формате YYYY-MM-DD")
    args = parser.parse_args()

    if not all([args.lat, args.lng, args.date]):
        print("Не все обязательные аргументы предоставлены.")
        parser.print_help()
        exit(1)

    results = call_api(args.lat, args.lng, args.date)
    save_json(results, f'{team_name}.json')
