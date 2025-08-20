FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1

# Install system basics + git (needed for LFS pull)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only requirements first
COPY requirements.txt /app/

RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . /app

# --- NEW: pull large files tracked by Git LFS ---
RUN git lfs install && git lfs pull || true

# Use fewer workers to avoid OOM on small instances
# (first 'app' = app.py filename, second 'app' = Flask object)
CMD gunicorn app:app --workers=1 --threads=4 --timeout=120 --bind 0.0.0.0:$PORT
