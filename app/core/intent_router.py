from typing import Optional

class IntentRouter:
    @staticmethod
    def route(message: str) -> Optional[str]:
        # Simple keyword-based routing
        if "time" in message.lower():
            return "time"
        elif "weather" in message.lower():
            return "weather"
        elif "memory" in message.lower():
            return "memory"
        elif "robot" in message.lower():
            return "robot"
        else:
            return "chat"