from typing import Any, Dict, Optional

from pydantic import BaseModel


class RobotCommandRequest(BaseModel):
    command: str
    params: Optional[Dict[str, Any]] = None


class RobotStatusResponse(BaseModel):
    battery: int
    mode: str
    estop: bool
    nav_state: str
    follow_enabled: bool = False
    manual_enabled: bool = False
    ros2_connected: bool = False
    active_source: str = "idle"
    last_command: str = "idle"
    buddybot_workspace: Optional[str] = None


class RobotCommandResponse(BaseModel):
    success: bool
    message: str
    status: Optional[RobotStatusResponse] = None
