#!/bin/bash

BASE_URL="http://localhost:8000"

echo "Testing /health"
curl -X GET "$BASE_URL/health"

echo -e "\n\nTesting /time"
curl -X GET "$BASE_URL/time"

echo -e "\n\nTesting /memory/save"
curl -X POST "$BASE_URL/memory/save" -H "Content-Type: application/json" -d '{"key": "test", "value": "value"}'

echo -e "\n\nTesting /memory/get"
curl -X GET "$BASE_URL/memory/get?key=test"

echo -e "\n\nTesting /robot/status"
curl -X GET "$BASE_URL/robot/status"