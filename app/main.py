from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes_chat import router as chat_router
from app.api.routes_health import router as health_router
from app.api.routes_memory import router as memory_router
from app.api.routes_navigation import router as navigation_router
from app.api.routes_robot import router as robot_router
from app.api.routes_time import router as time_router
from app.api.routes_weather import router as weather_router

app = FastAPI(
    title="BuddyBot AI",
    description="Voice-ready BuddyBot control panel with assistant and robot bridge",
)

app.include_router(health_router)
app.include_router(chat_router)
app.include_router(time_router)
app.include_router(weather_router)
app.include_router(memory_router)
app.include_router(navigation_router)
app.include_router(robot_router)

static_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def root():
    return FileResponse(static_dir / "index.html")


@app.get("/app-info")
def app_info():
    return JSONResponse(
        {
            "name": "BuddyBot Control App",
            "features": [
                "voice chat",
                "weather and time assistant",
                "memory save and recall",
                "manual teleop",
                "user follow toggle",
                "semantic waypoint save and go",
                "robot status dashboard",
            ],
        }
    )
