#!/bin/bash

# Activate virtual environment (support both .venv and venv)
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Error: Virtual environment not found. Please create one with 'python3 -m venv .venv' or 'python3 -m venv venv'"
    exit 1
fi

# Run the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload