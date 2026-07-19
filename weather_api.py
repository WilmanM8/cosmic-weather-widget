import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WEATHER_CODES = {
    0: ("Despejado", "☀️"),
    1: ("Mayormente despejado", "🌤️"),
    2: ("Parcialmente nublado", "⛅"),
    3: ("Nublado", "☁️"),
    45: ("Niebla", "🌫️"),
    48: ("Niebla escarcha", "🌫️"),
    51: ("Llovizna ligera", "🌧️"),
    53: ("Llovizna moderada", "🌧️"),
    55: ("Llovizna densa", "🌧️"),
    56: ("Llovizna helada ligera", "🌧️"),
    57: ("Llovizna helada densa", "🌧️"),
    61: ("Lluvia ligera", "🌧️"),
    63: ("Lluvia moderada", "🌧️"),
    65: ("Lluvia fuerte", "🌧️"),
    66: ("Lluvia helada ligera", "🌧️"),
    67: ("Lluvia helada fuerte", "🌧️"),
    71: ("Nieve ligera", "🌨️"),
    73: ("Nieve moderada", "🌨️"),
    75: ("Nieve fuerte", "🌨️"),
    77: ("Granizo", "🌨️"),
    80: ("Chubascos ligeros", "🌧️"),
    81: ("Chubascos moderados", "🌧️"),
    82: ("Chubascos violentos", "🌧️"),
    85: ("Chubascos de nieve ligeros", "🌨️"),
    86: ("Chubascos de nieve fuertes", "🌨️"),
    95: ("Tormenta", "⛈️"),
    96: ("Tormenta con granizo leve", "⛈️"),
    99: ("Tormenta con granizo fuerte", "⛈️"),
}

def get_location_by_ip():
    """Detects location using IP-API."""
    try:
        response = requests.get("http://ip-api.com/json/")
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "success":
            return {
                "city": data.get("city"),
                "lat": data.get("lat"),
                "lon": data.get("lon")
            }
        else:
            logger.error(f"IP-API Error: {data.get('message')}")
            return None
    except Exception as e:
        logger.error(f"Error fetching location: {e}")
        return None

def get_location_by_name(city_name):
    """Detects location using Open-Meteo Geocoding API."""
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=es&format=json"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        results = data.get("results")
        if results and len(results) > 0:
            return {
                "city": results[0].get("name"),
                "lat": results[0].get("latitude"),
                "lon": results[0].get("longitude")
            }
        else:
            logger.error(f"Geocoding Error: No se encontró la ciudad {city_name}")
            return None
    except Exception as e:
        logger.error(f"Error fetching location: {e}")
        return None

def get_location(configured_city):
    """Returns location either by name or IP if set to auto."""
    if not configured_city or configured_city.lower() == "auto":
        return get_location_by_ip()
    return get_location_by_name(configured_city)

def get_weather(lat, lon):
    """Fetches weather from Open-Meteo for the given coordinates."""
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        current = data.get("current_weather", {})
        
        temp = current.get("temperature", 0)
        code = current.get("weathercode", 0)
        desc, icon = WEATHER_CODES.get(code, ("Desconocido", "❓"))
        
        return {
            "temperature": temp,
            "description": desc,
            "icon": icon
        }
    except Exception as e:
        logger.error(f"Error fetching weather: {e}")
        return None

if __name__ == "__main__":
    loc = get_location_by_ip()
    if loc:
        print(f"Ubicación: {loc['city']} ({loc['lat']}, {loc['lon']})")
        weather = get_weather(loc['lat'], loc['lon'])
        if weather:
            print(f"Clima: {weather['temperature']}°C, {weather['description']} {weather['icon']}")
