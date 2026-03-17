from typing import Dict, Any
from app.schemas.robot import RobotStatusResponse
from app.logger import logger

class RobotTool:
    @staticmethod
    def get_status() -> RobotStatusResponse:
        # Mock status
        return RobotStatusResponse(
            battery=85,
            mode="idle",
            estop=False,
            nav_state="docked"
        )

    @staticmethod
    def execute_command(command: str, params: Dict[str, Any]) -> str:
        # Mock execution
        logger.info(f"Executing mock command: {command} with params: {params}")
        if command == "stop":
            return "Robot stopped"
        elif command == "dock":
            return "Robot docking"
        elif command == "move":
            x = params.get("x", 0)
            y = params.get("y", 0)
            return f"Robot moving to ({x}, {y})"
        else:
            return f"Unknown command: {command}"