# ==============================================================================
# PaisaPath AI - Production Multi-Stage Dockerfile for Nebius Cloud
# Combines React + Vite Frontend, FastAPI Backend, and Streamlit in one container.
# ==============================================================================

# ---------- Stage 1: Build Frontend Assets ----------
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build


# ---------- Stage 2: Final Production Runner ----------
FROM python:3.11-slim AS runner
WORKDIR /app

# Install system dependencies (curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt requirements-api.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-api.txt

# Copy application source code
COPY api.py app.py financial_engine.py market_data.py news_agent.py ai_agent.py db.py ./
COPY data/ ./data/
COPY .streamlit/ ./.streamlit/

# Copy built React frontend assets from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Copy entrypoint startup script
COPY start.sh ./start.sh
RUN chmod +x ./start.sh

# Default environment configuration
ENV PORT=8000
ENV PYTHONUNBUFFERED=1
ENV APP_MODE=api

# Expose ports:
# 8000 -> FastAPI Backend + React Frontend Dashboard
# 8501 -> Streamlit Dashboard
EXPOSE 8000 8501

# Healthcheck targeting FastAPI
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8000}/api/health || exit 1

ENTRYPOINT ["/app/start.sh"]

