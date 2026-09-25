# ── Multi-Stage Build for SATQuery AI ─────────────────────────────
# Stage 1: Build the React + Three.js Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend

# Install dependencies
COPY frontend/package*.json ./
RUN npm install --frozen-lockfile || npm install

# Build static bundle to /frontend/dist
COPY frontend/ ./
RUN npm run build

# ── Stage 2: Python Backend with FastAPI & Computer Vision ─────────
FROM python:3.11-slim
WORKDIR /app

# Install minimal system libraries for OpenCV and image processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy backend source code
COPY backend/ ./backend/

# Copy built frontend assets from Stage 1
COPY --from=frontend-builder /frontend/dist ./frontend/dist
COPY frontend/samples/ ./frontend/samples/

# Hugging Face Spaces uses port 7860 by default. Render/Railway provide $PORT.
ENV PORT=7860
EXPOSE 7860

# Launch FastAPI app with Uvicorn
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
