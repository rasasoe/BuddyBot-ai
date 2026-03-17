import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")
    SQLITE_PATH: str = os.getenv("SQLITE_PATH", "./data/buddybot.db")