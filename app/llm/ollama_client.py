from typing import Optional

import requests

from app.logger import logger


class OllamaClient:
    SYSTEM_PROMPT = """
당신은 BuddyBot 입니다.

BuddyBot은 사용자를 도와주는 이동형 AI 로봇 비서입니다.
항상 친절하고 자연스러운 한국어로 대답합니다.
자신을 Qwen이나 다른 모델명으로 소개하지 말고, "버디봇"이라고 소개하세요.

가능한 기능:
- 날씨 조회
- 시간 확인
- 메모 저장과 조회
- 로봇 상태 안내
- 이동, 정지, 추종 같은 안전한 로봇 제어

답변은 짧고 명확하게 하며, 안전이 필요한 동작은 신중하게 안내하세요.
"""

    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            return True
        except requests.RequestException:
            return False

    def generate(self, prompt: str) -> Optional[str]:
        try:
            full_prompt = f"{self.SYSTEM_PROMPT}\n\n사용자: {prompt}\n버디봇:"
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": full_prompt, "stream": False},
                timeout=45,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip() or None
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            return "응답 생성에 시간이 오래 걸리고 있어요. 잠시 후 다시 시도해 주세요."
        except requests.exceptions.ConnectionError:
            logger.warning("Failed to connect to Ollama")
            return None
        except requests.RequestException as exc:
            logger.error("Ollama request failed: %s", exc)
            return None
