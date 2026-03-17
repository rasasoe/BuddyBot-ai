from fastapi import FastAPI
from app.api.routes_health import router as health_router
from app.api.routes_chat import router as chat_router
from app.api.routes_time import router as time_router
from app.api.routes_weather import router as weather_router
from app.api.routes_memory import router as memory_router
from app.api.routes_robot import router as robot_router

app = FastAPI(title="BuddyBot AI", description="Jarvis-style AI assistant server")

app.include_router(health_router)
app.include_router(chat_router)
app.include_router(time_router)
app.include_router(weather_router)
app.include_router(memory_router)
app.include_router(robot_router)

@app.get("/")
def root():
    return {"message": "BuddyBot AI Server"}