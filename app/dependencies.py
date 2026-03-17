from app.config import Config
from app.logger import logger

def get_config() -> Config:
    return Config()

def get_logger():
    return logger