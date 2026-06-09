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

    @staticmethod
    def _fast_local_response(message: str) -> Optional[str]:
        text = message.lower().replace(" ", "")
        polite_text = message.lower().strip()

        if any(word in polite_text for word in ["안녕", "hello", "hi"]):
            return "안녕하세요. 저는 버디봇입니다. 무엇을 도와드릴까요?"

        if any(word in text for word in ["너는누구", "넌누구", "뭐하는로봇", "자기소개", "버디봇소개"]):
            return (
                "저는 사용자를 따라다니고 주변 공간을 인식하는 이동형 AI 비서 로봇, 버디봇입니다. "
                "음성 제어, 사용자 추종, LiDAR 미니맵, 날씨와 시간 안내를 할 수 있습니다."
            )

        if any(word in text for word in ["기능설명", "할수있는일", "뭐할수"]):
            return (
                "버디봇은 음성 명령으로 이동하고, 카메라로 사용자를 따라가며, "
                "LiDAR 미니맵으로 주변 장애물을 보여주고, 서버 AI로 날씨와 질문에 답합니다."
            )

        follow_question = any(word in text for word in ["추종설명", "사용자추종설명", "따라오는기능"])
        follow_question = follow_question or (
            "추종" in text and any(word in text for word in ["설명", "뭐야", "어떻게", "원리"])
        )
        if follow_question:
            return (
                "사용자 추종은 카메라로 사람을 감지하고 화면 중심과 거리 기준으로 따라가는 기능입니다. "
                "정지와 안전 판단은 Pi 로컬 제어가 우선합니다."
            )

        if any(word in text for word in ["미니맵", "lidar", "라이다"]):
            return (
                "미니맵은 LiDAR 거리 데이터를 2차원으로 보여주는 화면입니다. "
                "중앙은 로봇이고 주변 점들은 감지된 장애물입니다."
            )

        if "갈비찜" in text and any(word in text for word in ["레시피", "요리법", "만드는법", "만들어"]):
            return (
                "갈비찜은 갈비를 한번 데친 뒤 간장, 배나 사과, 마늘, 설탕, 참기름 양념에 재워 "
                "무와 당근을 넣고 약한 불에서 40분 정도 졸이면 됩니다. 마지막에 대파와 참기름을 넣으면 더 맛있습니다."
            )

        if any(word in text for word in ["레시피", "요리법", "만드는법"]):
            return "가능합니다. 재료 이름을 같이 말해 주시면 짧은 조리 순서로 알려드릴게요."

        return None

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

        fast_response = self._fast_local_response(message)
        if fast_response:
            return fast_response

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
