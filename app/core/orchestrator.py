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
            return (
                f"현재 배터리는 {status.battery}%이고 "
                f"모드는 {status.mode}, 추종은 {'켜짐' if status.follow_enabled else '꺼짐'}, "
                f"활성 제어 소스는 {status.active_source}입니다."
            )

        if intent == "robot_stop":
            return self.robot.execute_command("stop")["message"]

        if intent == "robot_dock":
            return self.robot.execute_command("dock")["message"]

        if intent == "robot_follow_start":
            return self.robot.execute_command("follow")["message"]

        if intent == "robot_follow_stop":
            return self.robot.execute_command("follow_stop")["message"]

        if intent == "robot_manual":
            return self.robot.execute_command(
                "manual",
                {
                    "direction": slots.get("direction", "forward"),
                    "speed": slots.get("speed", 0.3),
                    "duration": slots.get("duration", 1.5),
                },
            )["message"]

        if intent == "nav_goto":
            waypoint = slots.get("waypoint", "home_base")
            result = self.navigation.navigate_to(waypoint)
            return result["message"]

        if intent == "nav_save_waypoint":
            waypoint = slots.get("waypoint", "custom_point")
            saved = self.navigation.save_waypoint(
                name=waypoint,
                x=slots.get("x", 0.0),
                y=slots.get("y", 0.0),
                theta=slots.get("theta", 0.0),
                description=f"{waypoint} semantic checkpoint",
            )
            pose = saved.get("pose", {})
            return (
                f"{waypoint} 체크포인트를 저장했습니다. "
                f"x={pose.get('x')}, y={pose.get('y')}, theta={pose.get('theta')}입니다."
            )

        response = None
        if self.gemini is not None and self._is_complex(message):
            logger.info("Using Gemini for complex request")
            response = self.gemini.generate(message)

        if not response:
            response = self.ollama.generate(message)

        if response:
            return response
        return (
            "버디봇이에요. 지금은 로컬 응답 모드로 동작 중입니다. "
            "시간, 날씨, 메모, 추종 시작, 정지, 수동 이동 같은 명령은 바로 처리할 수 있어요."
        )
