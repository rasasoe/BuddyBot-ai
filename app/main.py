import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.background import BackgroundTask

from app.api.routes_chat import router as chat_router
from app.api.routes_health import router as health_router
from app.api.routes_memory import router as memory_router
from app.api.routes_navigation import router as navigation_router
from app.api.routes_robot import router as robot_router
from app.api.routes_time import router as time_router
from app.api.routes_weather import router as weather_router
from app.stt.whisper_service import WhisperService
from app.tts.speech_service import SpeechService

app = FastAPI(
    title="BuddyBot AI",
    description="Voice-ready BuddyBot control panel with assistant and robot bridge",
)

app.include_router(health_router)
app.include_router(chat_router)
app.include_router(time_router)
app.include_router(weather_router)
app.include_router(memory_router)
app.include_router(navigation_router)
app.include_router(robot_router)

static_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

stt_service = WhisperService()
tts_service = SpeechService()


class TTSRequest(BaseModel):
    text: str


@app.get("/")
def root():
    return FileResponse(static_dir / "index.html")


@app.get("/app-info")
def app_info():
    return JSONResponse(
        {
            "name": "BuddyBot Control App",
            "features": [
                "voice chat",
                "weather and time assistant",
                "memory save and recall",
                "manual teleop",
                "user follow toggle",
                "semantic waypoint save and go",
                "robot status dashboard",
                "optional offline whisper STT",
                "optional edge/piper TTS",
            ],
        }
    )


@app.post("/stt")
async def stt(request: Request):
    content_type = request.headers.get("content-type", "")
    if "multipart/form-data" in content_type:
        try:
            form = await request.form()
        except Exception as exc:
            raise HTTPException(status_code=503, detail=f"multipart parsing unavailable: {exc}") from exc
        upload = form.get("audio")
        if upload is None:
            raise HTTPException(status_code=400, detail="audio field is required")
        suffix = Path(getattr(upload, "filename", "") or "audio.wav").suffix or ".wav"
        payload = await upload.read()
    else:
        payload = await request.body()
        suffix = ".wav"

    if not payload:
        raise HTTPException(status_code=400, detail="audio payload is empty")

    fd, temp_name = tempfile.mkstemp(prefix="buddybot_stt_", suffix=suffix)
    os.close(fd)
    temp_path = Path(temp_name)
    try:
        temp_path.write_bytes(payload)
        try:
            text = stt_service.transcribe(str(temp_path))
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        return {"text": text}
    finally:
        temp_path.unlink(missing_ok=True)


@app.post("/tts")
async def tts(request: TTSRequest):
    try:
        result = await tts_service.synthesize_to_file(request.text)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return FileResponse(
        result["path"],
        media_type=result["media_type"],
        filename=Path(result["path"]).name,
        background=BackgroundTask(lambda: Path(result["path"]).unlink(missing_ok=True)),
    )
