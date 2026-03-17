from fastapi import APIRouter, Depends, HTTPException
from app.schemas.memory import MemorySaveRequest, MemoryGetResponse
from app.dependencies import get_config
from app.memory.store import MemoryStore

router = APIRouter()

@router.post("/memory/save")
def save_memory(request: MemorySaveRequest, config=Depends(get_config)):
    store = MemoryStore(config.SQLITE_PATH)
    store.save(request.key, request.value)
    return {"message": "Memory saved"}

@router.get("/memory/get", response_model=MemoryGetResponse)
def get_memory(key: str, config=Depends(get_config)):
    store = MemoryStore(config.SQLITE_PATH)
    value = store.get(key)
    if value is None:
        raise HTTPException(status_code=404, detail="Memory not found")
    return MemoryGetResponse(key=key, value=value)