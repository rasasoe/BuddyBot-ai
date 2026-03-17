from fastapi import APIRouter, Depends, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.dependencies import get_config
from app.llm.ollama_client import OllamaClient
from app.core.orchestrator import Orchestrator
from app.tools.weather_tool import WeatherTool
from app.memory.store import MemoryStore

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, config=Depends(get_config)):
    ollama = OllamaClient(config.OLLAMA_BASE_URL, config.OLLAMA_MODEL)
    weather = WeatherTool(config.OPENWEATHER_API_KEY)
    memory = MemoryStore(config.SQLITE_PATH)
    orchestrator = Orchestrator(ollama, weather, memory)
    
    response = orchestrator.process_message(request.message)
    if response is None:
        raise HTTPException(status_code=503, detail="LLM service unavailable")
    return ChatResponse(response=response)