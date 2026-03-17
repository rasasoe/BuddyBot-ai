from fastapi import APIRouter, Depends
from app.dependencies import get_config, get_logger
from app.llm.ollama_client import OllamaClient
from app.memory.store import MemoryStore
import sqlite3

router = APIRouter()

@router.get("/health")
def health_check(config=Depends(get_config), logger=Depends(get_logger)):
    # Check Ollama
    ollama_ok = False
    try:
        client = OllamaClient(config.OLLAMA_BASE_URL, config.OLLAMA_MODEL)
        # Simple ping
        response = client.generate("Hello")
        ollama_ok = response is not None
    except:
        ollama_ok = False

    # Check SQLite
    sqlite_ok = False
    try:
        store = MemoryStore(config.SQLITE_PATH)
        store.save("test", "test")
        value = store.get("test")
        sqlite_ok = value == "test"
    except:
        sqlite_ok = False

    return {
        "status": "healthy" if ollama_ok and sqlite_ok else "unhealthy",
        "ollama": "connected" if ollama_ok else "disconnected",
        "sqlite": "connected" if sqlite_ok else "disconnected"
    }