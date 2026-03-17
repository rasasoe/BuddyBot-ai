import requests
from typing import Optional
from app.config import Config
from app.logger import logger

class OllamaClient:
    SYSTEM_PROMPT = """
당신은 BuddyBot 입니다.

BuddyBot은 사용자를 도와주는 이동형 AI 로봇 비서입니다.
항상 한국어로만 답합니다.

절대 중국어로 답하지 않습니다.
절대 자신을 Qwen이라고 소개하지 않습니다.
자신을 "버디봇"이라고 소개합니다.

친절하고 자연스러운 한국어로 대화합니다.

BuddyBot은 다음 기능을 사용할 수 있습니다.

- 날씨 조회
- 시간 확인
- 메모 저장
- 로봇 상태 확인

가능하면 짧고 명확하게 답합니다.
"""

    def __init__(self, base_url: str, model: str):
        self.base_url = base_url
        self.model = model

    def generate(self, prompt: str) -> Optional[str]:
        try:
            full_prompt = f"{self.SYSTEM_PROMPT}\n\n사용자: {prompt}\n버디봇:"
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": full_prompt, "stream": False},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except requests.RequestException as e:
            logger.error(f"Ollama request failed: {e}")
            return None