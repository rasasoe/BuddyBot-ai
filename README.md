# BuddyBot-ai

`BuddyBot-ai`는 BuddyBot의 서버컴용 저장소입니다.

이 레포는 라즈베리파이 5에서 직접 돌리는 레포가 아니라, 서버 PC에서 실행하는 상위 제어/AI/웹앱 레포입니다.

이 저장소가 담당하는 기능:
- 메인 웹 GUI
- AI 채팅
- 브라우저 기반 음성 입력/출력 UX
- 시간, 날씨, 메모리 기능
- 체크포인트 목록/저장/이동 요청 API
- 로봇 고수준 명령 처리

아래 기능은 이 레포가 아니라 `BuddyBot` 레포가 담당합니다:
- ROS 2
- LiDAR
- 사용자 추종
- Nav2 / waypoint navigation
- Pi5 <-> Pico 시리얼 브리지
- Pico 모터 펌웨어

## 전체 시스템 역할 분리

- 서버컴: `BuddyBot-ai`
- 라즈베리파이 5: `BuddyBot`
- 라즈베리파이 Pico: `BuddyBot/firmware/pico_motor_controller`

## 이 레포로 가능한 것

- FastAPI 기반 웹 서버 실행
- 브라우저에서 메인 관제 화면 접속
- 수동 제어 명령 전송
- 추종 시작/중지 같은 상위 명령 전송
- 체크포인트 저장/이동/분석
- 브라우저 음성 인식 사용
- Ollama를 통한 로컬/원격 LLM 연동

## 이 레포로 직접 하지 않는 것

- 모터를 직접 구동하지 않음
- Pi5 ROS2 스택을 대체하지 않음
- Pico 펌웨어를 대체하지 않음
- Pi5/Pico 설정 없이 실제 로봇 주행을 보장하지 않음

## 권장 환경

- Python 3.11 이상
- 서버컴과 Pi5가 같은 네트워크에 연결되어 있으면 좋음
- 선택 사항: Ollama
- 선택 사항: OpenWeather API 키

## 설치 방법

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

설명:
- `OPENWEATHER_API_KEY`: 날씨 API 키
- `OLLAMA_BASE_URL`: Ollama 서버 주소
- `OLLAMA_MODEL`: 사용할 Ollama 모델명
- `SQLITE_PATH`: 메모리/상태 저장용 sqlite 경로
- `BUDDYBOT_REPO_PATH`: 로컬에 함께 받아놓은 `BuddyBot` 레포 경로
- `DEFAULT_CITY`: 기본 도시

## 실행 방법

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

브라우저 접속:
- 같은 PC: `http://127.0.0.1:8000`
- 같은 네트워크 다른 기기: `http://서버컴IP:8000`

## 메인 GUI에서 할 수 있는 것

- 수동 조작 패널
- 추종 시작 / 중지
- 체크포인트 저장
- 체크포인트 이동
- 미니맵 형태 체크포인트 분석
- 브라우저 음성 인식
- AI 채팅
- 로봇 상태 확인

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

3. 아래 항목을 순서대로 확인합니다.
- 정지 명령
- 수동 이동 버튼
- 추종 시작 / 중지
- 체크포인트 저장
- 체크포인트 이동
- 시간 / 날씨 질문

## 팀원용 빠른 설치

서버컴 담당 팀원은 아래만 실행하면 시작할 수 있습니다.

```bash
git clone https://github.com/rasasoe/BuddyBot-ai.git
cd BuddyBot-ai
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Pi5 단독 모드와의 관계

이 서버가 없어도 로봇은 기본 기능으로 동작할 수 있습니다.

서버컴이 없을 때:
- Pi5 단독 모드 사용 가능
- Pi5 로컬 UI 사용 가능
- Pi5 로컬 음성 명령 사용 가능
- 기본 수동 조작 / 추종 / 체크포인트 이동 가능

서버컴이 있을 때:
- Assistant Mode 사용 가능
- AI 채팅 가능
- 더 풍부한 음성 비서 기능 사용 가능
- 더 풍부한 웹 GUI 사용 가능

즉:
- `BuddyBot-ai`는 필수 모터 제어 레포가 아니라 상위 AI/관제 레포입니다.

## 테스트

```bash
python -m pytest tests
```

## 팀원들에게 꼭 같이 전달할 주의사항

이 레포는 설치와 소프트웨어 수준 검증을 시작하기에 충분히 정리되어 있습니다.

다만 실제 로봇 완성은 아래 하드웨어 검증이 추가로 필요합니다.
- 모터 방향 보정
- Kiwi drive 운동학 검증
- 실제 오도메트리 검증
- 사용자 추종 튜닝
- 실제 주행 네비게이션 튜닝

정리하면:
- 소프트웨어 구조와 GUI는 준비됨
- 실제 하드웨어 튜닝은 아직 현장 검증 필요

## 팀원이 같이 보면 좋은 파일

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
