from typing import Optional

from app.core.intent_router import IntentRouter
from app.llm.gemini_client import GeminiClient
from app.llm.ollama_client import OllamaClient
from app.logger import logger
from app.memory.store import MemoryStore
from app.tools.navigation_tool import NavigationTool
from app.tools.robot_tool import RobotTool
from app.tools.time_tool import TimeTool
from app.tools.weather_tool import WeatherTool


class Orchestrator:
    def __init__(
        self,
        ollama_client: OllamaClient,
        weather_tool: WeatherTool,
        time_tool: TimeTool,
        robot_tool: RobotTool,
        memory_store: MemoryStore,
        navigation_tool: NavigationTool,
        gemini_client: Optional[GeminiClient] = None,
    ):
        self.ollama = ollama_client
        self.gemini = gemini_client
        self.weather = weather_tool
        self.time = time_tool
        self.robot = robot_tool
        self.memory = memory_store
        self.navigation = navigation_tool

    def _local_robot_control_message(self) -> str:
        return (
            "로봇 이동 명령은 서버 AI가 직접 실행하지 않습니다. "
            "버디봇 전진, 멈춰, 따라와 같은 명령은 Pi 로컬 음성 제어에서 처리합니다."
        )

    def _is_complex(self, message: str) -> bool:
        text = message.strip().lower()
        if len(text) >= 80:
            return True
        complex_keywords = [
            "이유",
            "분석",
            "비교",
            "설명",
            "설명해줘",
            "정리",
            "방법",
            "코드",
            "어떻게",
            "왜",
        ]
        return any(keyword in text for keyword in complex_keywords)

    @staticmethod
    def _voice_safe(text: str, *, max_chars: int = 220) -> str:
        cleaned = " ".join((text or "").replace("```", " ").replace("*", " ").split()).strip()
        if len(cleaned) <= max_chars:
            return cleaned
        cut = cleaned[:max_chars].rsplit(" ", 1)[0].strip() or cleaned[:max_chars].strip()
        return f"{cut}. 자세한 내용은 패널에서 확인해 주세요."

    def process_message(self, message: str) -> str:
        intent = IntentRouter.route(message)
        slots = IntentRouter.extract_slots(message, intent)
        logger.info("Intent=%s slots=%s", intent, slots)

        if intent == "time":
            time_str = self.time.get_current_time("Asia/Seoul")
            return f"현재 시각은 {time_str}입니다."

        if intent == "weather":
            city = slots.get("city", "Seoul")
            weather_data = self.weather.get_weather(city)
            if weather_data:
                return self.weather.summarize_weather(city, weather_data)
            return "날씨 정보를 가져오지 못했습니다. API 또는 네트워크 상태를 확인해 주세요."

        if intent == "memory_save":
            content = slots.get("content", "").strip() or message.strip()
            key = slots.get("key", "user_memory")
            self.memory.save(key, content)
            return f"알겠습니다. '{content}' 내용을 기억해 둘게요."

        if intent == "memory_get":
            key = slots.get("key", "user_memory")
            content = self.memory.get(key)
            if content:
                return f"제가 기억하고 있는 내용은 '{content}'입니다."
            return "아직 저장된 메모가 없습니다."

        if intent == "robot_status":
            status = self.robot.get_status()
            follow_state = "켜짐" if status.follow_enabled else "꺼짐"
            return (
                f"현재 배터리는 {status.battery}퍼센트이고, 모드는 {status.mode}입니다. "
                f"사용자 추종은 {follow_state}입니다."
            )

        if intent in {
            "robot_stop",
            "robot_dock",
            "robot_follow_start",
            "robot_follow_stop",
            "robot_manual",
            "nav_goto",
        }:
            return self._local_robot_control_message()

        if intent == "nav_save_waypoint":
            return "체크포인트 저장은 Pi 패널에서 현재 위치를 기준으로 실행해 주세요."

        response = None
        if self.gemini is not None and self._is_complex(message):
            logger.info("Using Gemini for complex request")
            response = self.gemini.generate(message)

        if not response:
            response = self.ollama.generate(message)

        if response:
            return self._voice_safe(response)
        return (
            "저는 버디봇입니다. 시간, 날씨, 메모, 작품 설명은 서버가 답하고, "
            "이동과 정지는 Pi 로컬 제어가 처리합니다."
        )
