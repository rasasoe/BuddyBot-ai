from typing import Dict, Any
from app.logger import logger

class PolicyEngine:
    SAFE_COMMANDS = ["stop", "status", "dock", "follow", "move"]
    UNSAFE_COMMANDS = ["shutdown_motors_forever", "ignore_safety", "disable_estop"]

    @staticmethod
    def check_command(command: str) -> Dict[str, Any]:
        if command in PolicyEngine.UNSAFE_COMMANDS:
            logger.warning(f"Blocked unsafe command: {command}")
            return {"allowed": False, "reason": "Unsafe command blocked"}
        elif command in PolicyEngine.SAFE_COMMANDS:
            return {"allowed": True, "reason": "Command allowed"}
        else:
            logger.warning(f"Unknown command: {command}")
            return {"allowed": False, "reason": "Unknown command"}