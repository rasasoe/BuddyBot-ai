#!/bin/bash

# Activate virtual environment (assuming venv in project root)
source venv/bin/activate

# Run the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload