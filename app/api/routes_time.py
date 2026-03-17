from fastapi import APIRouter, Query
from app.tools.time_tool import TimeTool

router = APIRouter()

@router.get("/time")
def get_time(timezone: str = Query(None)):
    return {"time": TimeTool.get_current_time(timezone)}