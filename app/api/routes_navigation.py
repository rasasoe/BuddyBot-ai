from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.tools.navigation_tool import NavigationTool

router = APIRouter()
navigation = NavigationTool()


class WaypointSaveRequest(BaseModel):
    name: str
    x: float
    y: float
    theta: float = 0.0
    description: str = ""


class WaypointGoRequest(BaseModel):
    name: str


@router.get("/nav/waypoints")
def list_waypoints():
    return {"items": navigation.list_waypoints()}


@router.get("/nav/map-summary")
def map_summary():
    return navigation.analyze_map()


@router.post("/nav/waypoints")
def save_waypoint(request: WaypointSaveRequest):
    if not navigation.control_enabled:
        raise HTTPException(
            status_code=403,
            detail="Checkpoint writes are handled on the Pi panel in local robot mode",
        )
    waypoint = navigation.save_waypoint(
        request.name,
        request.x,
        request.y,
        request.theta,
        request.description,
    )
    return {"saved": True, "waypoint": waypoint}


@router.post("/nav/go")
def go_to_waypoint(request: WaypointGoRequest):
    if not navigation.control_enabled:
        raise HTTPException(
            status_code=403,
            detail="Waypoint movement is handled locally on the Pi",
        )
    return navigation.navigate_to(request.name)
