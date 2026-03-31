from fastapi import APIRouter, Depends

from app.dependencies import get_config
from app.llm.ollama_client import OllamaClient
from app.memory.store import MemoryStore
from app.tools.robot_tool import RobotTool

router = APIRouter()


@router.get("/health")
def health_check(config=Depends(get_config)):
    ollama = OllamaClient(config.OLLAMA_BASE_URL, config.OLLAMA_MODEL)
    store = MemoryStore(config.SQLITE_PATH)
    robot = RobotTool()

    sqlite_ok = False
    try:
        store.save("healthcheck", "ok")
        sqlite_ok = store.get("healthcheck") == "ok"
    except Exception:
        sqlite_ok = False

    return {
        "status": "healthy" if sqlite_ok else "degraded",
        "ollama": "connected" if ollama.is_available() else "disconnected",
        "sqlite": "connected" if sqlite_ok else "disconnected",
        "robot_bridge": "connected" if robot.use_ros2 else "mock",
    }
