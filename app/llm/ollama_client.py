import json
import time
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

    def __init__(
        self,
        base_url: str,
        model: str,
        *,
        timeout_sec: float = 30.0,
        keep_alive: str = "30m",
        num_predict: int = 64,
        num_ctx: int = 1024,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_sec = max(1.0, timeout_sec)
        self.keep_alive = keep_alive
        self.num_predict = max(16, num_predict)
        self.num_ctx = max(512, num_ctx)

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            return True
        except requests.RequestException:
            return False

    def warmup(self) -> bool:
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": "ping",
                    "stream": False,
                    "keep_alive": self.keep_alive,
                    "options": {
                        "temperature": 0.0,
                        "num_predict": 8,
                    },
                },
                timeout=max(self.timeout_sec, 45.0),
            )
            response.raise_for_status()
            logger.info("Ollama model warmed: %s", self.model)
            return True
        except requests.RequestException as exc:
            logger.warning("Ollama warmup failed: %s", exc)
            return False

    def generate(self, prompt: str) -> Optional[str]:
        try:
            full_prompt = f"{self.SYSTEM_PROMPT}\n\n사용자: {prompt}\n버디봇:"
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": True,
                    "keep_alive": self.keep_alive,
                    "options": {
                        "temperature": 0.2,
                        "num_predict": self.num_predict,
                        "num_ctx": self.num_ctx,
                    },
                },
                timeout=(3.0, self.timeout_sec),
                stream=True,
            )
            response.raise_for_status()
            return self._collect_stream(response)
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            return self._timeout_fallback(prompt)
        except requests.exceptions.ConnectionError:
            logger.warning("Failed to connect to Ollama")
            return None
        except requests.RequestException as exc:
            logger.error("Ollama request failed: %s", exc)
            return None

    def _collect_stream(self, response: requests.Response) -> Optional[str]:
        chunks = []
        started_at = time.monotonic()
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            token = payload.get("response", "")
            if token:
                chunks.append(token)
            text = "".join(chunks).strip()
            if len(text) >= 220:
                return text[:220].rsplit(" ", 1)[0].strip() or text[:220].strip()
            if len(text) >= 45 and text[-1:] in ".!?。？！요다":
                return text
            if time.monotonic() - started_at > self.timeout_sec and text:
                logger.warning("Returning partial Ollama response after timeout window")
                return text
            if payload.get("done"):
                return text or None
        return "".join(chunks).strip() or None

    @staticmethod
    def _timeout_fallback(prompt: str) -> str:
        text = prompt.lower().replace(" ", "")
        if "코딩" in text:
            return "코딩은 컴퓨터에게 일을 시키기 위해 순서와 규칙을 글로 적는 작업입니다. 쉽게 말하면 프로그램을 만드는 방법이에요."
        if "뭐하면" in text or "뭐하지" in text or "심심" in text:
            return "가볍게 산책하거나 물 한 잔 마시고, 오늘 할 일을 하나만 정해보는 게 좋아요. 원하면 제가 짧게 계획도 같이 잡아드릴게요."
        return "좋아요. 그 주제로 짧게 이야기해볼게요. 지금은 답변을 간단히 줄여서 말하겠습니다."
