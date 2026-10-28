# PaisaPath AI — React frontend

This frontend is designed around the existing PaisaPath repository.

The existing backend already contains:
- `financial_engine.py` — deterministic financial calculations
- `market_data.py` — AMFI NAV search/history and clearly marked demo stock data
- `news_agent.py` — Tavily news retrieval
- `ai_agent.py` — NVIDIA Nemotron through Nebius Token Factory
- `app.py` — original Streamlit UI

## 1. Put the files into the repository

Copy:
- `frontend/` into the PaisaPath repository
- `api.py` into the repository root
- `requirements-api.txt` into the repository root

Do not delete the existing Python files.

## 2. Start the Python API

From the PaisaPath root:

```bash
pip install -r requirements.txt
pip install -r requirements-api.txt
uvicorn api:app --reload --port 8000
```

The API should open at:

`http://localhost:8000/api/health`

## 3. Start the React frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown by the terminal, normally:

`http://localhost:5173`

## 4. Environment variables

The frontend can optionally use:

```bash
VITE_API_BASE=http://localhost:8000
```

The frontend does NOT contain your Nebius or Tavily keys.

Keep those keys in the Python backend `.env`.

The existing project uses:
- `NEBIUS_API_KEY`
- `NEBIUS_BASE_URL`
- `NEBIUS_MODEL`
- `TAVILY_API_KEY`

## 5. Important architecture rule

Do not duplicate financial calculations in React.

The React app sends profile inputs to `/api/affordability`, which calls the existing
`financial_engine.savings_capacity()` function.

Likewise, AI requests go through `ai_agent.ask_nemotron()` so the Nebius/Nemotron
runtime call remains in the Python backend.

## 6. Current UI

The frontend contains:
- Dashboard
- Affordability checker
- Goal planner
- Portfolio scenario simulator
- Mutual fund/NAV search and history
- News search + AI explanation
- PaisaPath AI Coach

If the API is unavailable, several screens intentionally fall back to demo values so
you can design/test the UI before connecting credentials.

## 7. Hackathon safety

Keep the existing honesty rules:
- AMFI NAV = latest published NAV, not live.
- Stock data = DEMO until a licensed provider is connected.
- The LLM explains supplied facts; it should not do financial arithmetic.
- Never expose API keys in React/Vite environment variables that are shipped to users.
