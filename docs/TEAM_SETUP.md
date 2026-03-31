# BuddyBot AI Team Setup

## Role

`BuddyBot-ai` runs on the server PC.

It provides:
- the web GUI
- chat and voice UX
- weather, time, memory, waypoint analysis
- high-level robot commands

## Requirements

- Python 3.11 or newer
- Network access from Pi 5 to the server PC
- Optional: Ollama for local LLM replies

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
```

## Run

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open:

- local PC: `http://127.0.0.1:8000`
- from Pi 5 or other device: `http://SERVER_PC_IP:8000`

## Main GUI features

- manual drive pad
- follow mode toggle
- browser voice recognition
- AI chat
- waypoint save and go
- mini-map and checkpoint analysis

## Important routes

- `GET /health`
- `POST /chat`
- `GET /robot/status`
- `POST /robot/command`
- `GET /nav/waypoints`
- `POST /nav/waypoints`
- `POST /nav/go`
- `GET /nav/map-summary`

## Quick test

```bash
python -m pytest tests
```

## Team handoff note

The server PC repo does not directly drive motors.
It should send high-level commands while the Pi 5 handles ROS2, LiDAR, follow, and motor control.

