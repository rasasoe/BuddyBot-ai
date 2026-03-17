from pydantic import BaseModel

class MemorySaveRequest(BaseModel):
    key: str
    value: str

class MemoryGetResponse(BaseModel):
    key: str
    value: str