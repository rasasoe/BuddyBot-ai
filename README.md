# BuddyBot AI

BuddyBot AI는 서버컴에서 실행하는 버디봇의 상위 제어 서버입니다.

이 저장소는 다음 역할을 담당합니다.
- 웹 GUI 제공
- 음성/텍스트 기반 AI 대화
- 날씨, 시간, 메모리 기능
- 체크포인트 목록/저장/분석
- 로봇에 대한 고수준 명령 전달

실제 LiDAR, ROS2, 추종, 모터 제어는 `BuddyBot` 저장소와 Raspberry Pi 5/Pico 쪽에서 담당합니다.

## 역할 분리

- 서버컴: `BuddyBot-ai`
- Raspberry Pi 5: `BuddyBot`
- Raspberry Pi Pico: `BuddyBot/firmware/pico_motor_controller`

## 주요 기능

- 실제품 스타일 웹 관제 화면
- 수동 조작 버튼
- 사용자 추종 시작/중지
- 음성 입력과 브라우저 음성 출력
- AI 채팅
- 체크포인트 저장과 이동
- 미니맵 스타일 체크포인트 분석

## 요구 사항

- Python 3.11 이상
- Windows, Ubuntu, macOS 중 하나
- 선택 사항: Ollama
- 선택 사항: OpenWeather API Key

## 설치

```bash
git clone https://github.com/rasasoe/BuddyBot-ai.git
cd BuddyBot-ai
python -m pip install -r requirements.txt
```

## 환경 변수

필요하면 `.env` 파일을 만들어 사용합니다.

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

- 서버컴 로컬: `http://127.0.0.1:8000`
- 같은 네트워크 다른 장치: `http://서버컴IP:8000`

## GUI에서 할 수 있는 것

- 수동 조작
- 추종 시작 / 추종 중지
- 도킹 / 정지
- 음성 인식 기반 대화
- 체크포인트 선택 이동
- 체크포인트 저장
- 미니맵 분석 확인

## 주요 API

- `GET /health`
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

## 빠른 테스트

```bash
python -m pytest tests
```

## 팀원 설치 안내

팀원은 서버컴에서 아래만 하면 됩니다.

```bash
git clone https://github.com/rasasoe/BuddyBot-ai.git
cd BuddyBot-ai
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

자세한 설치 문서는 아래 파일을 참고하세요.

- `docs/TEAM_SETUP.md`

## 프로젝트 구조

```text
BuddyBot-ai/
├── app/
│   ├── api/
│   ├── core/
│   ├── llm/
│   ├── memory/
│   ├── schemas/
│   ├── static/
│   ├── tools/
│   └── main.py
├── docs/
├── scripts/
├── tests/
├── requirements.txt
└── README.md
```

## 참고

이 저장소는 로봇의 저수준 모터 제어를 직접 하지 않습니다.
실제 주행 정확도, LiDAR, odom, follow, waypoint 실행은 `BuddyBot` 저장소에서 담당해야 합니다.

