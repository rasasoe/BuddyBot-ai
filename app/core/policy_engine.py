from typing import Any, Dict

from app.logger import logger


class PolicyEngine:
    SAFE_COMMANDS = [
        "status",
    ]
    ROBOT_CONTROL_COMMANDS = [
        "stop",
        "dock",
        "follow",
        "follow_start",
        "follow_stop",
        "unfollow",
        "move",
        "manual",
        "navigate",
        "goto",
        "save_waypoint",
    ]
    UNSAFE_COMMANDS = ["shutdown_motors_forever", "ignore_safety", "disable_estop"]

    @staticmethod
    def check_command(command: str) -> Dict[str, Any]:
        normalized = command.lower().strip()
        if normalized in PolicyEngine.UNSAFE_COMMANDS:
            logger.warning("Blocked unsafe command: %s", normalized)
            return {"allowed": False, "reason": "Unsafe command blocked"}
        if normalized in PolicyEngine.ROBOT_CONTROL_COMMANDS:
            logger.warning("Blocked server-side robot control command: %s", normalized)
            return {"allowed": False, "reason": "Robot control commands are handled locally on the Pi"}
        if normalized in PolicyEngine.SAFE_COMMANDS:
            return {"allowed": True, "reason": "Command allowed"}
        logger.warning("Unknown command: %s", normalized)
        return {"allowed": False, "reason": "Unknown command"}
