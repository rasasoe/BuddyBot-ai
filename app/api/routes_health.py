from fastapi import APIRouter, Depends

from app.config import Config
from app.dependencies import get_config
from app.llm.gemini_client import GeminiClient
from app.llm.ollama_client import OllamaClient
from app.memory.store import MemoryStore
from app.stt.whisper_service import WhisperService
from app.tools.robot_tool import RobotTool
from app.tts.speech_service import SpeechService

router = APIRouter()


@router.get("/health")
def health_check(config: Config = Depends(get_config)):
    ollama = OllamaClient(config.OLLAMA_BASE_URL, config.OLLAMA_MODEL)
    gemini = GeminiClient(config.GEMINI_API_KEY, config.GEMINI_MODEL)
    stt = WhisperService()
    tts = SpeechService()
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
        "gemini": "configured" if gemini.is_configured() else "not_configured",
        "sqlite": "connected" if sqlite_ok else "disconnected",
        "robot_bridge": "connected" if robot.use_ros2 else "mock",
        "stt": "available" if stt.is_available() else "not_installed",
        "tts": tts.status(),
    }
