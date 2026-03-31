from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import get_config
from app.tools.weather_tool import WeatherTool

router = APIRouter()


@router.get("/weather")
def get_weather(city: str = Query(...), config=Depends(get_config)):
    weather_tool = WeatherTool(config.OPENWEATHER_API_KEY)
    data = weather_tool.get_weather(city)
    if not data:
        raise HTTPException(status_code=503, detail="Weather service unavailable")

    return {
        "city": city,
        "raw_data": data,
        "summary": weather_tool.summarize_weather(city, data),
    }
