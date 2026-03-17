from pydantic import BaseModel
from typing import Dict, Any, Optional

class RobotCommandRequest(BaseModel):
    command: str
    params: Optional[Dict[str, Any]] = None

class RobotStatusResponse(BaseModel):
    battery: int
    mode: str
    estop: bool
    nav_state: str

class RobotCommandResponse(BaseModel):
    success: bool
    message: str