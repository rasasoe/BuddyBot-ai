from __future__ import annotations

import asyncio
import subprocess
import tempfile
from pathlib import Path
from typing import Dict

from app.config import Config

try:
    import edge_tts
except ImportError:  # pragma: no cover - optional dependency
    edge_tts = None


class SpeechService:
    def __init__(self):
        self.config = Config()

    def status(self) -> Dict[str, object]:
        return {
            "edge_tts": edge_tts is not None,
            "piper_model": bool(self.config.PIPER_MODEL_PATH),
            "backend": self.config.TTS_BACKEND,
        }

    def is_available(self) -> bool:
        return edge_tts is not None or bool(self.config.PIPER_MODEL_PATH)

    async def synthesize_to_file(self, text: str) -> Dict[str, str]:
        cleaned = " ".join(text.split()).strip()
        if not cleaned:
            raise RuntimeError("text is empty")

        backend = self.config.TTS_BACKEND.lower().strip()
        if backend in {"auto", "edge"} and edge_tts is not None:
            return await self._synthesize_with_edge(cleaned)
        if backend in {"auto", "piper"} and self.config.PIPER_MODEL_PATH:
            return await asyncio.to_thread(self._synthesize_with_piper, cleaned)
        raise RuntimeError("no TTS backend is configured")

    async def _synthesize_with_edge(self, text: str) -> Dict[str, str]:
        temp_path = Path(tempfile.mkstemp(prefix="buddybot_tts_", suffix=".mp3")[1])
        communicator = edge_tts.Communicate(
            text=text,
            voice=self.config.EDGE_TTS_VOICE,
            rate=self.config.EDGE_TTS_RATE,
        )
        await communicator.save(str(temp_path))
        return {"path": str(temp_path), "media_type": "audio/mpeg"}

    def _synthesize_with_piper(self, text: str) -> Dict[str, str]:
        temp_path = Path(tempfile.mkstemp(prefix="buddybot_tts_", suffix=".wav")[1])
        command = [
            self.config.PIPER_BIN,
            "--model",
            self.config.PIPER_MODEL_PATH,
            "--output_file",
            str(temp_path),
        ]
        completed = subprocess.run(
            command,
            input=text,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if completed.returncode != 0:
            stderr = (completed.stderr or completed.stdout or "").strip()
            raise RuntimeError(stderr or f"piper exited with {completed.returncode}")
        return {"path": str(temp_path), "media_type": "audio/wav"}
