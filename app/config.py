import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _default_buddybot_repo() -> str:
    return str((Path(__file__).resolve().parents[2] / "BuddyBot").resolve())


class Config:
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")
    SQLITE_PATH: str = os.getenv("SQLITE_PATH", "./data/buddybot.db")
    BUDDYBOT_REPO_PATH: str = os.getenv("BUDDYBOT_REPO_PATH", _default_buddybot_repo())
    DEFAULT_CITY: str = os.getenv("DEFAULT_CITY", "Seoul")

    STT_MODEL_SIZE: str = os.getenv("STT_MODEL_SIZE", "tiny")
    STT_DEVICE: str = os.getenv("STT_DEVICE", "cpu")
    STT_COMPUTE_TYPE: str = os.getenv("STT_COMPUTE_TYPE", "int8")
    STT_LANGUAGE: str = os.getenv("STT_LANGUAGE", "ko")

    TTS_BACKEND: str = os.getenv("TTS_BACKEND", "auto")
    EDGE_TTS_VOICE: str = os.getenv("EDGE_TTS_VOICE", "ko-KR-SunHiNeural")
    EDGE_TTS_RATE: str = os.getenv("EDGE_TTS_RATE", "+0%")
    PIPER_BIN: str = os.getenv("PIPER_BIN", "piper")
    PIPER_MODEL_PATH: str = os.getenv("PIPER_MODEL_PATH", "")
