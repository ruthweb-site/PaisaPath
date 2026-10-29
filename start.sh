#!/bin/bash
set -e

echo "=========================================================="
echo " Starting PaisaPath AI Container in Mode: '${APP_MODE:-api}'"
echo "=========================================================="

if [ "$APP_MODE" = "streamlit" ]; then
    echo "Launching Streamlit Dashboard on port ${PORT:-8501}..."
    exec streamlit run app.py --server.port="${PORT:-8501}" --server.address=0.0.0.0

elif [ "$APP_MODE" = "both" ]; then
    echo "Launching Streamlit Dashboard on port 8501 in background..."
    streamlit run app.py --server.port=8501 --server.address=0.0.0.0 &
    
    echo "Launching FastAPI + React Dashboard on port ${PORT:-8000}..."
    exec uvicorn api:app --host 0.0.0.0 --port "${PORT:-8000}"

else
    # Default: FastAPI backend hosting both API endpoints and React SPA
    echo "Launching FastAPI + React Dashboard on port ${PORT:-8000}..."
    exec uvicorn api:app --host 0.0.0.0 --port "${PORT:-8000}"
fi

