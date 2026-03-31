import re
from typing import Any, Dict, Optional


class IntentRouter:
    WEATHER_CITIES = {
        "서울": "Seoul",
        "seoul": "Seoul",
        "부산": "Busan",
        "busan": "Busan",
        "대구": "Daegu",
        "daegu": "Daegu",
        "인천": "Incheon",
        "incheon": "Incheon",
        "대전": "Daejeon",
        "daejeon": "Daejeon",
        "광주": "Gwangju",
        "gwangju": "Gwangju",
        "제주": "Jeju",
        "jeju": "Jeju",
    }

    @staticmethod
    def route(message: str) -> Optional[str]:
        text = message.lower()

        if any(word in text for word in ["날씨", "weather", "기온", "온도"]):
            return "weather"
        if any(word in text for word in ["시간", "몇 시", "몇시", "time", "시각"]):
            return "time"
        if any(word in text for word in ["기억해", "저장해", "메모해", "save", "remember"]):
            return "memory_save"
        if any(word in text for word in ["뭐 저장", "불러", "기억한", "메모 보여", "retrieve", "recall"]):
            return "memory_get"
        if any(word in text for word in ["상태", "배터리", "robot status", "status"]) and "날씨" not in text:
            return "robot_status"
        if any(word in text for word in ["정지", "멈춰", "스톱", "stop"]):
            return "robot_stop"
        if any(word in text for word in ["도킹", "충전", "dock", "charger"]):
            return "robot_dock"
        if any(word in text for word in ["추종 시작", "따라와", "follow me", "follow on"]):
            return "robot_follow_start"
        if any(word in text for word in ["추종 중지", "따라오지마", "follow off", "unfollow"]):
            return "robot_follow_stop"
        if any(word in text for word in ["체크포인트", "웨이포인트", "waypoint"]) and any(
            word in text for word in ["저장", "기록", "save", "create"]
        ):
            return "nav_save_waypoint"
        if any(word in text for word in ["이동", "가줘", "가자", "navigate", "go to", "안내해"]):
            if any(word in text for word in ["주방", "방", "거실", "문", "도어", "home", "base", "kitchen", "bedroom"]):
                return "nav_goto"
        if any(word in text for word in ["앞으로", "뒤로", "왼쪽", "오른쪽", "manual", "수동"]):
            return "robot_manual"
        return "chat"

    @staticmethod
    def extract_slots(message: str, intent: str) -> Dict[str, Any]:
        text = message.lower()
        slots: Dict[str, Any] = {}

        if intent == "weather":
            slots["city"] = IntentRouter._extract_city(text) or "Seoul"
        elif intent == "memory_save":
            slots["key"] = "user_memory"
            slots["content"] = IntentRouter._extract_memory_content(message)
        elif intent == "memory_get":
            slots["key"] = "user_memory"
        elif intent == "robot_manual":
            slots["direction"] = IntentRouter._extract_direction(text)
            duration_match = re.search(r"(\d+(?:\.\d+)?)\s*초", message)
            speed_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:속도|speed)", text)
            slots["duration"] = float(duration_match.group(1)) if duration_match else 1.5
            slots["speed"] = float(speed_match.group(1)) if speed_match else 0.3
        elif intent == "nav_goto":
            slots["waypoint"] = IntentRouter._extract_waypoint_name(message)
        elif intent == "nav_save_waypoint":
            slots["waypoint"] = IntentRouter._extract_waypoint_name(message)
            x_match = re.search(r"x\s*=?\s*(-?\d+(?:\.\d+)?)", text)
            y_match = re.search(r"y\s*=?\s*(-?\d+(?:\.\d+)?)", text)
            theta_match = re.search(r"(?:theta|yaw|각도)\s*=?\s*(-?\d+(?:\.\d+)?)", text)
            slots["x"] = float(x_match.group(1)) if x_match else 0.0
            slots["y"] = float(y_match.group(1)) if y_match else 0.0
            slots["theta"] = float(theta_match.group(1)) if theta_match else 0.0

        return slots

    @staticmethod
    def _extract_city(text: str) -> Optional[str]:
        for token, city in IntentRouter.WEATHER_CITIES.items():
            if token in text:
                return city
        return None

    @staticmethod
    def _extract_memory_content(message: str) -> str:
        for marker in ["기억해줘", "기억해", "저장해줘", "저장해", "메모해줘", "메모해"]:
            if marker in message:
                return message.split(marker, 1)[0].strip() or "사용자 메모"
        return message.strip()

    @staticmethod
    def _extract_direction(text: str) -> str:
        if "뒤로" in text or "backward" in text:
            return "backward"
        if "왼쪽" in text or "left" in text:
            return "left"
        if "오른쪽" in text or "right" in text:
            return "right"
        return "forward"

    @staticmethod
    def _extract_waypoint_name(message: str) -> str:
        text = message.lower()
        mapping = {
            "주방": "kitchen",
            "부엌": "kitchen",
            "거실": "living_room_center",
            "안방": "bedroom",
            "방": "bedroom",
            "현관": "front_door",
            "문": "front_door",
            "충전": "charging_station",
            "충전소": "charging_station",
            "홈": "home_base",
            "베이스": "home_base",
            "kitchen": "kitchen",
            "bedroom": "bedroom",
            "home": "home_base",
            "base": "home_base",
        }
        for key, value in mapping.items():
            if key in text:
                return value

        match = re.search(r"(?:체크포인트|웨이포인트)\s+([a-zA-Z0-9_\-가-힣]+)", message)
        if match:
            return match.group(1).strip().replace(" ", "_")
        return "home_base"
