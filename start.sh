#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "🚀 Starting OutboundAI..."

# Load .env only if it exists (local dev). On Render, env vars come from the dashboard.
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | grep -v '^\s*$' | xargs)
fi

# Render assigns $PORT dynamically. Fall back to 8000 for local dev.
APP_PORT="${PORT:-8000}"

echo "📋 Configuration:"
echo "   LiveKit:  ${LIVEKIT_URL:-NOT SET}"
echo "   Gemini:   ${GEMINI_MODEL:-gemini-2.0-flash-exp}"
echo "   Supabase: ${SUPABASE_URL:-NOT SET}"
echo "   Port:     ${APP_PORT}"

echo "🌐 Starting FastAPI server on port ${APP_PORT}..."
uvicorn server:app --host 0.0.0.0 --port "${APP_PORT}" &
SERVER_PID=$!

sleep 2

echo "🤖 Starting LiveKit agent worker..."
python agent.py start

kill $SERVER_PID 2>/dev/null || true
