FROM python:3.11-slim

# --------------------
# System dependencies
# --------------------
# Install FFmpeg development libraries so the Python 'av' package can build if a wheel is not available.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ffmpeg libavformat-dev libavcodec-dev libavdevice-dev \
       libavutil-dev libavfilter-dev libswscale-dev libswresample-dev \
       build-essential pkg-config \
    && rm -rf /var/lib/apt/lists/*

# --------------------
# Python environment setup
# --------------------
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=0 \
    PORT=8000

WORKDIR /app

# Install Python dependencies first for better layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the application code
COPY . .

EXPOSE 8000

# --------------------
# Start the application with Gunicorn (Uvicorn workers)
# --------------------
CMD gunicorn -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:${PORT} 