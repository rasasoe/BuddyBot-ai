import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _default_buddybot_repo() -> str:
    return str((Path(__file__).resolve().parents[2] / "BuddyBot").resolve())


class Config:
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")
    SQLITE_PATH: str = os.getenv("SQLITE_PATH", "./data/buddybot.db")
    BUDDYBOT_REPO_PATH: str = os.getenv("BUDDYBOT_REPO_PATH", _default_buddybot_repo())
    DEFAULT_CITY: str = os.getenv("DEFAULT_CITY", "Seoul")
