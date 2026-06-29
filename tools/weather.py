import logging
import os
import requests
import time
from dotenv import load_dotenv
from langchain.tools import tool


load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def _get_coordinates_nominatim(city: str) -> tuple[float, float, str]:
    """Retourne (lat, lon, nom_officiel) via Nominatim OSM."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": city, "format": "json", "limit": 1}
    headers = {"User-Agent": "MonAgentIA/1.0 (contact@mondomaine.com)"}  # ⚠️ obligatoire

    response = requests.get(url, params=params, headers=headers, timeout=10)
    time.sleep(1) # pour éviter de taper le rate limit
    response.raise_for_status()
    results = response.json()

    if not results:
        raise ValueError(f"Ville introuvable : {city}")

    loc = results[0]
    lat, lon = float(loc["lat"]), float(loc["lon"])
    city_name = loc["display_name"].split(",")[0]
    logger.info(f"Géocodage OK — {city_name} → lat: {lat:.4f}, lon: {lon:.4f}")

    return lat, lon, city_name


@tool
def get_weather(city: str) -> str:
    """Retourne la météo actuelle et les coordonnées GPS pour une ville donnée."""

    api_key = os.getenv("API_KEY_WEATHER")

    if not api_key:
        logger.error("API_KEY_WEATHER non définie.")
        return "Erreur : API_KEY_WEATHER non définie."
    
    try:
        lat, lon, city_name = _get_coordinates_nominatim(city)

        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=fr"
        )
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        result = (
            f"Météo à {city_name} (lat: {lat:.4f}, lon: {lon:.4f}) : "
            f"{data['weather'][0]['description']}, "
            f"{data['main']['temp']}°C, ressenti {data['main']['feels_like']}°C, "
            f"humidité {data['main']['humidity']}%"
        )
        logger.info(result)

        return result

    except ValueError as e:
        logger.error(f"Erreur géocodage : {e}")

        return f"Erreur géocodage : {e}"
    
    except requests.HTTPError as e:
        logger.error(f"Erreur HTTP {e.response.status_code}")

        return f"Erreur HTTP {e.response.status_code}"

