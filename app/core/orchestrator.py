from typing import Optional
from app.llm.ollama_client import OllamaClient
from app.tools.weather_tool import WeatherTool
from app.tools.time_tool import TimeTool
from app.tools.robot_tool import RobotTool
from app.memory.store import MemoryStore
from app.core.intent_router import IntentRouter
from app.core.policy_engine import PolicyEngine
from app.logger import logger

class Orchestrator:
    def __init__(self, ollama_client: OllamaClient, weather_tool: WeatherTool, memory_store: MemoryStore):
        self.ollama = ollama_client
        self.weather = weather_tool
        self.memory = memory_store

    def process_message(self, message: str) -> str:
        intent = IntentRouter.route(message)
        if intent == "time":
            return TimeTool.get_current_time()
        elif intent == "weather":
            # Assume city from message, simple
            city = "Seoul"  # Placeholder
            weather_data = self.weather.get_weather(city)
            if weather_data:
                summary = self._summarize_weather(weather_data)
                return f"Weather in {city}: {summary}"
            else:
                return "Weather data unavailable"
        elif intent == "memory":
            # Simple memory query
            return "Memory functionality"
        elif intent == "robot":
            return "Robot functionality"
        else:
            response = self.ollama.generate(message)
            return response or "Sorry, I couldn't generate a response"

    def _summarize_weather(self, data: dict) -> str:
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        return f"Temperature: {temp}°C, {desc}"