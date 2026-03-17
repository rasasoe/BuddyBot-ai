from fastapi import APIRouter, Depends, HTTPException
from app.schemas.robot import RobotCommandRequest, RobotStatusResponse, RobotCommandResponse
from app.tools.robot_tool import RobotTool
from app.core.policy_engine import PolicyEngine

router = APIRouter()

@router.get("/robot/status", response_model=RobotStatusResponse)
def get_robot_status():
    return RobotTool.get_status()

@router.post("/robot/command", response_model=RobotCommandResponse)
def execute_robot_command(request: RobotCommandRequest):
    policy = PolicyEngine.check_command(request.command)
    if not policy["allowed"]:
        raise HTTPException(status_code=403, detail=policy["reason"])
    
    result = RobotTool.execute_command(request.command, request.params or {})
    return RobotCommandResponse(success=True, message=result)