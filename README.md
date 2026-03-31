# BuddyBot-ai

`BuddyBot-ai`는 서버컴용 저장소입니다.

이 레포는 라즈베리파이 5에서 직접 돌리는 레포가 아니라, 서버 PC에서 실행하는 상위 AI/관제/웹앱 레포입니다.

## 담당 기능

- 메인 웹 GUI
- AI 채팅
- 브라우저 기반 음성 입력/출력
- 시간, 날씨, 메모리 기능
- 체크포인트 목록/저장/이동 API
- 체크포인트 기반 미니맵 분석
- 로봇 고수준 명령 처리

아래 기능은 `BuddyBot` 레포가 담당합니다.
- ROS 2
- LiDAR
- 사용자 추종
- Nav2 / waypoint navigation
- Pi5 <-> Pico 시리얼 브리지
- Pico 펌웨어

## 역할 분리

- 서버컴: `BuddyBot-ai`
- 라즈베리파이 5: `BuddyBot`
- 라즈베리파이 Pico: `BuddyBot/firmware/pico_motor_controller`

## 이 레포로 가능한 것

- FastAPI 웹 서버 실행
- 브라우저에서 메인 관제 화면 접속
- 수동 제어 명령 전송
- 추종 시작 / 중지 같은 상위 명령 전송
- 체크포인트 저장 / 이동 / 미니맵 분석
- 브라우저 음성 인식
- Ollama 기반 LLM 연동

## 이 레포가 직접 하지 않는 것

- 모터를 직접 구동하지 않음
- Pi5 ROS2 스택을 대체하지 않음
- Pico 펌웨어를 대체하지 않음

## 권장 환경

- Python 3.11 이상
- 선택 사항: Ollama
- 선택 사항: OpenWeather API 키

## 설치

```bash
git clone https://github.com/rasasoe/BuddyBot-ai.git
cd BuddyBot-ai
python -m pip install -r requirements.txt
```

## 선택 환경 변수

필요하면 `.env` 파일을 만들어 아래 값을 넣어 사용할 수 있습니다.

```bash
OPENWEATHER_API_KEY=your_key
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
SQLITE_PATH=./data/buddybot.db
BUDDYBOT_REPO_PATH=../BuddyBot
DEFAULT_CITY=Seoul
```

## 실행

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

브라우저 접속:
- 같은 PC: `http://127.0.0.1:8000`
- 같은 네트워크 다른 기기: `http://서버컴IP:8000`

## GUI에서 되는 것

- 수동 조작
- 사용자 추종 시작 / 중지
- 즉시 정지 / 도킹 명령
- 체크포인트 저장 / 이동
- 체크포인트 기반 미니맵 분석
- 미니맵 클릭 좌표 선택
- 음성 입력
- AI 대화

## 주요 API

- `GET /health`
- `GET /app-info`
- `POST /chat`
- `GET /time`
- `GET /weather`
- `POST /memory/save`
- `GET /memory/get`
- `GET /robot/status`
- `POST /robot/command`
- `GET /nav/waypoints`
- `POST /nav/waypoints`
- `POST /nav/go`
- `GET /nav/map-summary`

## 기본 사용 순서

1. 서버를 실행합니다.

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

2. 브라우저에서 GUI에 접속합니다.

3. 아래를 순서대로 확인합니다.
- 정지 명령
- 수동 이동
- 추종 시작 / 중지
- 체크포인트 저장
- 체크포인트 이동
- 시간 / 날씨 질문

## BuddyBot과의 관계

`BuddyBot-ai`는 없어도 로봇이 오프라인 기본 기능으로 동작할 수 있습니다.

서버컴이 없을 때:
- Pi5 단독 모드 사용 가능
- Pi5 로컬 UI 사용 가능
- 기본 수동 조작 / 체크포인트 / LiDAR 회피 시연 가능

서버컴이 있을 때:
- Assistant Mode 사용 가능
- AI 채팅 사용 가능
- 더 풍부한 음성 비서 기능 사용 가능
- 더 풍부한 통합 GUI 사용 가능

즉:
- `BuddyBot`만으로도 오프라인 시연 가능
- `BuddyBot-ai`는 AI 비서/상위 관제 확장용

## 테스트

```bash
python -m pytest tests
```

## 팀원에게 전달할 핵심

1. 오프라인 시연은 `BuddyBot`만으로 가능
2. 서버컴은 AI 비서 모드용
3. 서버 GUI는 시연/관제/설명용으로 사용
4. 실제 주행 정확도는 여전히 하드웨어 검증이 필요

## 중요한 현실적 주의사항

이 레포는 설치와 소프트웨어 수준 시연을 시작하기에 충분합니다.

하지만 실제 로봇 완성에는 아래 검증이 추가로 필요합니다.
- 모터 방향 보정
- Kiwi drive 운동학 검증
- 실제 오도메트리 검증
- 추종 튜닝
- 네비게이션 튜닝

## 같이 보면 좋은 파일

- `README.md`
- `docs/TEAM_SETUP.md`

## 폴더 구조

```text
BuddyBot-ai/
  app/
    api/
    core/
    llm/
    memory/
    schemas/
    static/
    tools/
    main.py
  docs/
  scripts/
  tests/
  requirements.txt
  README.md
```
