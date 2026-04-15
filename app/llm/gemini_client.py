from typing import Optional

import requests

from app.logger import logger


class GeminiClient:
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key.strip()
        self.model = model.strip() or "gemini-2.5-flash"

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def generate(self, prompt: str) -> Optional[str]:
        if not self.api_key:
            return None

        try:
            response = requests.post(
                (
                    "https://generativelanguage.googleapis.com/v1beta/models/"
                    f"{self.model}:generateContent?key={self.api_key}"
                ),
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.4,
                        "maxOutputTokens": 512,
                    },
                },
                timeout=45,
            )
            response.raise_for_status()
            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                return None
            parts = candidates[0].get("content", {}).get("parts", [])
            text = "".join(part.get("text", "") for part in parts).strip()
            return text or None
        except requests.RequestException as exc:
            logger.warning("Gemini request failed: %s", exc)
            return None
