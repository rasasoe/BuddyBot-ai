import re
from fastapi import FastAPI
from app.api.routes_health import router as health_router
from app.api.routes_chat import router as chat_router
from app.api.routes_time import router as time_router
from app.api.routes_weather import router as weather_router
from app.api.routes_memory import router as memory_router
from app.api.routes_robot import router as robot_router
from fastapi.responses import FileResponse
from pydantic import BaseModel
import subprocess
import os

app = FastAPI(title="BuddyBot AI", description="Jarvis-style AI assistant server")

app.include_router(health_router)
app.include_router(chat_router)
app.include_router(time_router)
app.include_router(weather_router)
app.include_router(memory_router)
app.include_router(robot_router)

@app.get("/")
def root():
    return {"message": "BuddyBot AI Server"}
    
class TTSRequest(BaseModel):
    text: str

@app.post("/tts")
async def generate_tts(req: TTSRequest):
    print(f"🗣️ [원래 답변] {req.text}")
    
    # 🚨 [핵심!] 텍스트 정제 필터 (외계어 방지)
    # 한글, 숫자, 공백, 기본 구두점(.,?!)만 남기고 한자/영어/마크다운 싹 다 지움!
    clean_text = re.sub(r'[^가-힣0-9\s\.\,\?\!]', '', req.text)
    
    # 파이퍼가 줄바꿈에서 음성을 뚝 끊어먹는 것을 방지
    clean_text = clean_text.replace('\n', ' ').strip()
    
    print(f"🧹 [정제된 답변] {clean_text}")

    output_file = os.path.abspath("server_reply.wav")
    piper_exe = os.path.expanduser("~/piper/piper")
    model_path = os.path.expanduser("~/piper/piper-kss-korean.onnx")
    
    try:
        subprocess.run(
            [piper_exe, "--model", model_path, "--output_file", output_file],
            input=clean_text.encode('utf-8'),
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return FileResponse(output_file, media_type="audio/wav")
    
    except subprocess.CalledProcessError as e:
        print(f"🚨 TTS 변환 실패: {e}")
        return {"error": "TTS generation failed"}