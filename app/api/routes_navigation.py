from fastapi import APIRouter
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
    return navigation.navigate_to(request.name)
