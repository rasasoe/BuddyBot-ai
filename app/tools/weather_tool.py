import requests
from typing import Optional, Dict, Any
from app.config import Config
from app.logger import logger

class WeatherTool:
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_weather(self, city: str) -> Optional[Dict[str, Any]]:
        if not self.api_key:
            logger.warning("OpenWeather API key not set")
            return None
        try:
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric",
                "lang": "kr"
            }
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Weather API request failed: {e}")
            return None