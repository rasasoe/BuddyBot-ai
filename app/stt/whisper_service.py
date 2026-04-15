from __future__ import annotations

from typing import Optional

from app.config import Config

try:
    from faster_whisper import WhisperModel
except ImportError:  # pragma: no cover - optional dependency
    WhisperModel = None


class WhisperService:
    def __init__(
        self,
        model_size: Optional[str] = None,
        device: Optional[str] = None,
        compute_type: Optional[str] = None,
        language: Optional[str] = None,
    ):
        config = Config()
        self.model_size = model_size or config.STT_MODEL_SIZE
        self.device = device or config.STT_DEVICE
        self.compute_type = compute_type or config.STT_COMPUTE_TYPE
        self.language = language or config.STT_LANGUAGE
        self._model = None

    def is_available(self) -> bool:
        return WhisperModel is not None

    def _load_model(self):
        if WhisperModel is None:
            raise RuntimeError("faster-whisper is not installed")
        if self._model is None:
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
            )
        return self._model

    def transcribe(self, audio_file: str) -> str:
        model = self._load_model()
        segments, _ = model.transcribe(
            audio_file,
            language=self.language,
            beam_size=1,
            vad_filter=True,
        )
        text = "".join(segment.text for segment in segments).strip()
        if not text:
            raise RuntimeError("speech was detected but no transcript was produced")
        return text
