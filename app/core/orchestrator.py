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
    def __init__(self, ollama_client: OllamaClient, weather_tool: WeatherTool, time_tool: TimeTool, robot_tool: RobotTool, memory_store: MemoryStore):
        self.ollama = ollama_client
        self.weather = weather_tool
        self.time = time_tool
        self.robot = robot_tool
        self.memory = memory_store

    def process_message(self, message: str) -> str:
        intent = IntentRouter.route(message)
        slots = IntentRouter.extract_slots(message, intent)
        
        if intent == "time":
            time_str = self.time.get_current_time()
            return f"현재 시각은 {time_str}입니다."
        elif intent == "weather":
            city = slots.get("city", "Seoul")
            weather_data = self.weather.get_weather(city)
            if weather_data:
                temp = weather_data["main"]["temp"]
                desc = weather_data["weather"][0]["description"]
                return f"현재 {city}은(는) {desc} 상태이고 기온은 {temp}°C입니다."
            else:
                return "날씨 정보를 가져올 수 없습니다."
        elif intent == "memory_save":
            content = slots.get("content", "")
            key = slots.get("key", "user_memory")
            self.memory.save(key, content)
            return f"알겠습니다. '{content}'를 저장해둘게요."
        elif intent == "memory_get":
            key = slots.get("key", "user_memory")
            content = self.memory.get(key)
            if content:
                return f"저장된 내용은 '{content}'입니다."
            else:
                return "저장된 내용이 없습니다."
        elif intent == "robot_status":
            status = self.robot.get_status()
            return f"현재 배터리는 {status.battery}%, 모드는 {status.mode}, 비상정지는 {status.estop}, 네비게이션 상태는 {status.nav_state}입니다."
        else:
            # General chat
            response = self.ollama.generate(message)
            return response or "죄송합니다. 응답을 생성할 수 없습니다."

    def _summarize_weather(self, data: dict) -> str:
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        return f"Temperature: {temp}°C, {desc}"