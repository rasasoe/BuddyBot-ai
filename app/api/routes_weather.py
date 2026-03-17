from fastapi import APIRouter, Query, Depends, HTTPException
from app.dependencies import get_config
from app.tools.weather_tool import WeatherTool
from app.llm.ollama_client import OllamaClient

router = APIRouter()

@router.get("/weather")
def get_weather(city: str = Query(...), config=Depends(get_config)):
    weather_tool = WeatherTool(config.OPENWEATHER_API_KEY)
    data = weather_tool.get_weather(city)
    if not data:
        raise HTTPException(status_code=503, detail="Weather service unavailable")
    
    # Summarize with LLM
    ollama = OllamaClient(config.OLLAMA_BASE_URL, config.OLLAMA_MODEL)
    prompt = f"Summarize this weather data in Korean: {data}"
    summary = ollama.generate(prompt) or f"온도: {data['main']['temp']}°C, 날씨: {data['weather'][0]['description']}"
    
    return {
        "city": city,
        "raw_data": data,
        "summary": summary
    }