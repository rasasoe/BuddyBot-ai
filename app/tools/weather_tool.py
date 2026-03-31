from typing import Any, Dict, Optional

import requests

from app.logger import logger


class WeatherTool:
    OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
    WTTR_URL = "https://wttr.in/{city}"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_weather(self, city: str) -> Optional[Dict[str, Any]]:
        if self.api_key:
            data = self._from_openweather(city)
            if data:
                return data

        return self._from_wttr(city)

    def summarize_weather(self, city: str, data: Dict[str, Any]) -> str:
        main = data.get("main", {})
        weather = data.get("weather", [{}])[0]
        temp = main.get("temp")
        desc = weather.get("description", "정보 없음")
        feels_like = main.get("feels_like")

        parts = [f"{city} 현재 날씨는 {desc}"]
        if temp is not None:
            parts.append(f"기온은 {temp}도")
        if feels_like is not None:
            parts.append(f"체감은 {feels_like}도")
        return ", ".join(parts) + "입니다."

    def _from_openweather(self, city: str) -> Optional[Dict[str, Any]]:
        try:
            response = requests.get(
                self.OPENWEATHER_URL,
                params={"q": city, "appid": self.api_key, "units": "metric", "lang": "kr"},
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            logger.warning("OpenWeather request failed: %s", exc)
            return None

    def _from_wttr(self, city: str) -> Optional[Dict[str, Any]]:
        try:
            response = requests.get(
                self.WTTR_URL.format(city=city),
                params={"format": "j1"},
                timeout=10,
            )
            response.raise_for_status()
            raw = response.json()
            current = raw.get("current_condition", [{}])[0]
            desc_items = current.get("lang_ko") or current.get("weatherDesc") or [{"value": "정보 없음"}]
            return {
                "main": {
                    "temp": self._safe_float(current.get("temp_C")),
                    "feels_like": self._safe_float(current.get("FeelsLikeC")),
                },
                "weather": [{"description": desc_items[0]["value"]}],
                "provider": "wttr.in",
                "raw": raw,
            }
        except requests.RequestException as exc:
            logger.error("Fallback weather request failed: %s", exc)
            return None

    @staticmethod
    def _safe_float(value: Any) -> Optional[float]:
        try:
            return float(value) if value is not None else None
        except (TypeError, ValueError):
            return None
