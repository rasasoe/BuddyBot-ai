from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
import app.main as main_module

client = TestClient(app)


def _temp_dir() -> Path:
    root = Path(__file__).resolve().parents[1] / ".test_tmp" / "voice_routes"
    root.mkdir(parents=True, exist_ok=True)
    return root


def test_stt_route_returns_transcript(monkeypatch):
    monkeypatch.setattr(main_module.stt_service, "transcribe", lambda _: "버디봇 테스트")

    response = client.post(
        "/stt",
        content=b"fake-wav-data",
        headers={"Content-Type": "audio/wav"},
    )

    assert response.status_code == 200
    assert response.json()["text"] == "버디봇 테스트"


def test_tts_route_returns_audio(monkeypatch):
    audio_path = _temp_dir() / "reply.mp3"
    audio_path.write_bytes(b"ID3")

    async def fake_synthesize(_: str):
        return {"path": str(audio_path), "media_type": "audio/mpeg"}

    monkeypatch.setattr(main_module.tts_service, "synthesize_to_file", fake_synthesize)

    response = client.post("/tts", json={"text": "안녕하세요"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("audio/mpeg")
    assert response.content == b"ID3"
