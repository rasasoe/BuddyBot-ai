from fastapi import APIRouter, Depends

from app.core.orchestrator import Orchestrator
from app.dependencies import get_config
from app.llm.gemini_client import GeminiClient
from app.llm.ollama_client import OllamaClient
from app.memory.store import MemoryStore
from app.schemas.chat import ChatRequest, ChatResponse
from app.tools.navigation_tool import NavigationTool
from app.tools.robot_tool import RobotTool
from app.tools.time_tool import TimeTool
from app.tools.weather_tool import WeatherTool

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, config=Depends(get_config)):
    orchestrator = Orchestrator(
        ollama_client=OllamaClient(config.OLLAMA_BASE_URL, config.OLLAMA_MODEL),
        gemini_client=GeminiClient(config.GEMINI_API_KEY, config.GEMINI_MODEL),
        weather_tool=WeatherTool(config.OPENWEATHER_API_KEY),
        time_tool=TimeTool(),
        robot_tool=RobotTool(),
        memory_store=MemoryStore(config.SQLITE_PATH),
        navigation_tool=NavigationTool(),
    )
    response = orchestrator.process_message(request.message)
    return ChatResponse(response=response)
