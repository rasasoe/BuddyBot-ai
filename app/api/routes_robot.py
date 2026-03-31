from fastapi import APIRouter, HTTPException

from app.core.policy_engine import PolicyEngine
from app.schemas.robot import RobotCommandRequest, RobotCommandResponse, RobotStatusResponse
from app.tools.robot_tool import RobotTool

router = APIRouter()
robot_tool = RobotTool()


@router.get("/robot/status", response_model=RobotStatusResponse)
def get_robot_status():
    return robot_tool.get_status()


@router.post("/robot/command", response_model=RobotCommandResponse)
def execute_robot_command(request: RobotCommandRequest):
    policy = PolicyEngine.check_command(request.command)
    if not policy["allowed"]:
        raise HTTPException(status_code=403, detail=policy["reason"])

    result = robot_tool.execute_command(request.command, request.params or {})
    return RobotCommandResponse(
        success=result["success"],
        message=result["message"],
        status=result.get("status"),
    )
