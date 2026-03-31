# BuddyBot AI

BuddyBot AI is the server-side control and assistant app for BuddyBot.

This repository is meant to run on the server PC, not on the Raspberry Pi 5.

It provides:
- the main web GUI
- AI chat
- browser-based voice UX
- weather, time, and memory features
- waypoint list and map summary APIs
- high-level robot commands

Low-level robot control, ROS 2, LiDAR, follow mode, and Pico motor control belong to the `BuddyBot` repository.

## System split

- Server PC: `BuddyBot-ai`
- Raspberry Pi 5: `BuddyBot`
- Raspberry Pi Pico: `BuddyBot/firmware/pico_motor_controller`

## What this repo does

- Runs a FastAPI web app
- Shows the main control dashboard
- Lets users send manual commands and high-level commands
- Supports voice input from the browser
- Supports checkpoint save, checkpoint go, and map summary
- Can talk to a local or remote LLM through Ollama

## What this repo does not do

- It does not directly drive motors
- It does not replace the Pi 5 ROS 2 stack
- It does not replace Pico firmware
- It does not guarantee real robot motion without Pi 5 and Pico setup

## Requirements

- Python 3.11 or newer
- Network access from Pi 5 to the server PC if assistant mode is used
- Optional: Ollama
- Optional: OpenWeather API key

## Install

```bash
git clone https://github.com/rasasoe/BuddyBot-ai.git
cd BuddyBot-ai
python -m pip install -r requirements.txt
```

## Optional environment file

Create `.env` if needed:

```bash
OPENWEATHER_API_KEY=your_key
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
SQLITE_PATH=./data/buddybot.db
BUDDYBOT_REPO_PATH=../BuddyBot
DEFAULT_CITY=Seoul
```

## Run

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open in a browser:

- same machine: `http://127.0.0.1:8000`
- same network: `http://SERVER_PC_IP:8000`

## Main GUI features

- manual drive panel
- follow mode start and stop
- checkpoint save
- checkpoint go
- mini-map style checkpoint analysis
- browser speech recognition
- AI chat
- robot status view

## Main API routes

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

## Basic usage

1. Start the server:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

2. Open the GUI in a browser.

3. Test:
- manual stop
- follow start and stop
- save a checkpoint
- go to a checkpoint
- ask for time or weather

## Team handoff quick start

For a teammate setting up only the server PC:

```bash
git clone https://github.com/rasasoe/BuddyBot-ai.git
cd BuddyBot-ai
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Relationship to Pi 5 local mode

The robot can still work without this server.

Without the server PC:
- Pi 5 can still run standalone mode
- local control on Pi 5 can still work
- local voice command mode on Pi 5 can still work

With the server PC:
- assistant mode becomes available
- AI chat and advanced voice assistant features become available
- the richer dashboard becomes available

## Testing

```bash
python -m pytest tests
```

## Important note for the team

This repository is ready for install and software-level testing.

However, real robot validation still depends on:
- motor direction calibration
- kiwi drive kinematics verification
- odometry verification on hardware
- follow tuning on hardware
- navigation tuning on hardware

That means:
- software structure is ready
- real hardware tuning is still required

## Files that teammates should read

- `README.md`
- `docs/TEAM_SETUP.md`

## Project layout

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

