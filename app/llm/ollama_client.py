from typing import Optional

import requests

from app.logger import logger


class OllamaClient:
    SYSTEM_PROMPT = """
당신은 BuddyBot입니다.

BuddyBot은 사용자를 따라다니며 주변 공간을 인식하는 이동형 AI 비서 로봇입니다.
답변은 한국어로 짧고 또렷하게 말하세요.
로봇 음성으로 읽기 쉬워야 하므로 기본 답변은 1~2문장으로 제한하세요.
마크다운, 코드블록, JSON, 특수기호, 긴 목록은 사용하지 마세요.
자신을 모델명으로 소개하지 말고 "버디봇"이라고 소개하세요.

가능한 기능:
- 날씨 조회
- 시간 확인
- 메모 저장과 조회
- 버디봇 기능 설명
- LiDAR 미니맵, 사용자 추종, 로컬 안전 제어 설명

전진, 정지, 추종 시작 같은 실제 이동 명령은 서버가 직접 실행하지 않습니다.
이동 명령은 Raspberry Pi 5의 로컬 음성 제어와 패널이 처리한다고 안내하세요.
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
            return "응답 생성 시간이 오래 걸리고 있습니다. 잠시 후 다시 말씀해 주세요."
        except requests.exceptions.ConnectionError:
            logger.warning("Failed to connect to Ollama")
            return None
        except requests.RequestException as exc:
            logger.error("Ollama request failed: %s", exc)
            return None
