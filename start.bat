@echo off
echo Starting OutboundAI...
start "FastAPI Server" uvicorn server:app --host 0.0.0.0 --port 8000
start "LiveKit Agent" python agent.py start
