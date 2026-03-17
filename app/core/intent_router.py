from typing import Optional, Dict, Any

class IntentRouter:
    @staticmethod
    def route(message: str) -> Optional[str]:
        text = message.lower()
        if any(word in text for word in ["날씨", "weather", "기온", "온도"]):
            return "weather"
        elif any(word in text for word in ["몇 시", "시간", "time", "시각"]):
            return "time"
        elif any(word in text for word in ["기억해", "저장해", "save", "memory"]):
            return "memory_save"
        elif any(word in text for word in ["불러와", "뭐 저장", "get", "retrieve"]):
            return "memory_get"
        elif any(word in text for word in ["배터리", "로봇 상태", "robot", "status"]):
            return "robot_status"
        else:
            return "chat"

    @staticmethod
    def extract_slots(message: str, intent: str) -> Dict[str, Any]:
        text = message.lower()
        slots = {}
        if intent == "weather":
            if "서울" in text:
                slots["city"] = "Seoul"
            elif "부산" in text:
                slots["city"] = "Busan"
            elif "대구" in text:
                slots["city"] = "Daegu"
            else:
                slots["city"] = "Seoul"  # default
        elif intent == "memory_save":
            # Simple extraction: assume the text before "기억해" or "저장해"
            if "기억해" in message:
                parts = message.split("기억해", 1)
                slots["content"] = parts[0].strip()
            elif "저장해" in message:
                parts = message.split("저장해", 1)
                slots["content"] = parts[0].strip()
            else:
                slots["content"] = message  # fallback
            slots["key"] = "user_memory"  # simple key
        elif intent == "memory_get":
            slots["key"] = "user_memory"  # simple key
        # time and robot_status don't need slots
        return slots