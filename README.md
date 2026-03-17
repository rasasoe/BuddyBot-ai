# BuddyBot AI

Jarvis 스타일의 로컬 AI 비서 서버. Raspberry Pi 5 기반 BuddyBot 로봇의 AI 서버 역할을 수행합니다.

## 프로젝트 개요

- **목표**: 로컬 AI 비서 서버
- **플랫폼**: Ubuntu 24.04
- **하드웨어**: RTX 4070 Ti (VRAM 11GB)
- **LLM**: Ollama 기반 qwen2.5:7b
- **STT**: faster-whisper 기반 (향후 구현)
- **TTS**: Piper 기반 (향후 구현)
- **API**: FastAPI
- **저장소**: SQLite
- **로봇 연동**: ROS2 bridge 준비 (현재 mock)

## 주요 기능

1. 일반 대화 (Ollama LLM)
2. 시간 조회 (타임존 지원)
3. 날씨 조회 (OpenWeatherMap API)
4. 메모리 저장/조회 (SQLite)
5. 로봇 상태 조회 (mock)
6. 로봇 명령 실행 (mock, 정책 검사)

## 설치 및 실행

### 1. 환경 설정

```bash
# Python 3.11 가상환경 생성
python3.11 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경변수 설정

`.env` 파일을 생성하고 `.env.example`을 참고하여 설정:

```bash
cp .env.example .env
# .env 파일 편집
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
OPENWEATHER_API_KEY=your_api_key_here
SQLITE_PATH=./data/buddybot.db
```

### 3. Ollama 설치 및 모델 다운로드

```bash
# Ollama 설치 (Ubuntu)
curl -fsSL https://ollama.ai/install.sh | sh

# 모델 다운로드
ollama pull qwen2.5:7b

# Ollama 서버 실행 (백그라운드)
ollama serve
```

### 4. 서버 실행

```bash
# 개발 모드
./scripts/dev_run.sh

# 또는 직접 실행
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. Docker 실행

```bash
# Docker Compose로 실행
docker-compose up --build
```

## API 엔드포인트

### GET /health
서버 상태 확인 (Ollama, SQLite 연결 상태)

**응답 예시:**
```json
{
  "status": "healthy",
  "ollama": "connected",
  "sqlite": "connected"
}
```

### POST /chat
일반 대화

**요청:**
```json
{
  "message": "안녕하세요"
}
```

**응답:**
```json
{
  "response": "안녕하세요! 무엇을 도와드릴까요?"
}
```

### GET /time
현재 시간 조회

**쿼리 파라미터:**
- `timezone` (optional): 타임존 (예: Asia/Seoul)

**응답:**
```json
{
  "time": "2024-01-01 12:00:00 UTC"
}
```

### GET /weather
날씨 조회

**쿼리 파라미터:**
- `city`: 도시명

**응답:**
```json
{
  "city": "Seoul",
  "raw_data": {...},
  "summary": "서울의 현재 날씨는 맑음, 온도는 15°C입니다."
}
```

### POST /memory/save
메모리 저장

**요청:**
```json
{
  "key": "reminder",
  "value": "내일 회의 2시"
}
```

### GET /memory/get
메모리 조회

**쿼리 파라미터:**
- `key`: 키

**응답:**
```json
{
  "key": "reminder",
  "value": "내일 회의 2시"
}
```

### GET /robot/status
로봇 상태 조회 (mock)

**응답:**
```json
{
  "battery": 85,
  "mode": "idle",
  "estop": false,
  "nav_state": "docked"
}
```

### POST /robot/command
로봇 명령 실행 (mock, 정책 검사)

**요청 예시:**
```json
{
  "command": "stop"
}
```

**응답:**
```json
{
  "success": true,
  "message": "Robot stopped"
}
```

## 테스트

```bash
# 모든 테스트 실행
pytest

# 특정 테스트
pytest tests/test_health.py
```

## 스모크 테스트

```bash
./scripts/smoke_test.sh
```

## 환경변수 설명

- `OLLAMA_BASE_URL`: Ollama 서버 URL (기본: http://localhost:11434)
- `OLLAMA_MODEL`: 사용할 LLM 모델 (기본: qwen2.5:7b)
- `OPENWEATHER_API_KEY`: OpenWeatherMap API 키
- `SQLITE_PATH`: SQLite 데이터베이스 경로 (기본: ./data/buddybot.db)

## 아키텍처

```
buddybot-ai/
├── app/
│   ├── main.py              # FastAPI 앱
│   ├── config.py            # 환경변수 설정
│   ├── logger.py            # 로깅 설정
│   ├── dependencies.py      # FastAPI 의존성
│   ├── api/                 # API 라우터
│   ├── core/                # 핵심 로직
│   │   ├── orchestrator.py  # 메인 오케스트레이터
│   │   ├── intent_router.py # 인텐트 라우팅
│   │   └── policy_engine.py # 정책 엔진
│   ├── llm/                 # LLM 클라이언트
│   ├── tools/               # 도구들
│   ├── memory/              # 메모리 저장소
│   ├── stt/                 # STT 서비스 (stub)
│   └── tts/                 # TTS 서비스 (stub)
├── tests/                   # 테스트
├── scripts/                 # 스크립트
└── data/                    # 데이터 디렉토리
```

## 향후 ROS2 연동 계획

1. **ROS2 노드 추가**: `app/ros/` 디렉토리 생성
2. **토픽 퍼블리셔/서브스크라이버**: 로봇 상태/명령 통신
3. **서비스 인터페이스**: ROS2 서비스로 API 확장
4. **실시간 데이터**: 센서 데이터 실시간 처리
5. **네비게이션 연동**: move_base 등과 통합

### STT/TTS 연동 방법

1. **STT (faster-whisper)**:
   - `pip install faster-whisper`
   - 오디오 입력 처리
   - WhisperService 구현

2. **TTS (Piper)**:
   - Piper 바이너리 설치
   - 텍스트 입력 처리
   - PiperService 구현

3. **API 확장**:
   - `/stt/transcribe` POST
   - `/tts/synthesize` POST

## 개발 노트

- 모든 코드는 타입힌트 포함
- 예외처리 및 로깅 구현
- 모듈화된 구조로 확장 용이
- 현재 로봇 기능은 mock으로 구현 (실제 하드웨어 제어 없음)
- 정책 엔진으로 위험 명령 차단

## 라이선스

MIT License