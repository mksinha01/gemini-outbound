FROM python:3.11-slim

# System dependencies required by LiveKit audio plugins
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 \
        libglib2.0-0 \
        libsndfile1 \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Pre-download Silero VAD model so agent starts instantly
RUN python -c "from livekit.plugins import silero; silero.VAD.load()" 2>/dev/null || true

COPY . .

# Render sets PORT dynamically. Default to 8000 for local dev.
ENV PORT=8000

EXPOSE ${PORT}

# start.sh reads $PORT and runs uvicorn + agent worker
CMD ["sh", "start.sh"]
