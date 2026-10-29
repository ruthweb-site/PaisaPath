# PaisaPath AI 🧭
**Your AI Financial Companion — From First Salary to Financial Freedom**  
*Built for the Nebius × NVIDIA Global AI Hackathon (Best Apps & Agents Track)*

---

## 💡 Overview

Millions of ordinary salaried Indians want to invest, but lack confidence, clear guidance on affordable amounts, and understanding of market volatility. **PaisaPath AI** prioritizes affordability before investing:
1. Calculates disposable income, emergency reserves, and debt constraints deterministically.
2. Uses **NVIDIA Nemotron** (`nvidia/Llama-3_1-Nemotron-Ultra-253B-v1`) via **Nebius Token Factory** to provide plain-language, source-aware financial explanations.
3. Incorporates **Tavily Search** to retrieve live financial news with publication timestamp reconciliation.
4. Integrates live **AMFI India** mutual fund NAV feeds.
5. Employs **SQLite** persistence for user profiles, saved goals, and audited portfolios.

---

## 🏛️ System Architecture

```
                  USER
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
┌──────────────────┐  ┌──────────────────┐
│  Streamlit App   │  │   React + Vite   │
│   (port 8501)    │  │   (port 5173)    │
└────────┬─────────┘  └────────┬─────────┘
         │                     │ HTTP
         │                     ▼
         │            ┌──────────────────┐
         │            │  FastAPI Backend │
         │            │   (port 8000)    │
         │            └────────┬─────────┘
         └──────────┬──────────┘
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
┌──────────────┐ ┌────────────┐ ┌────────────────┐
│  Financial   │ │Market Data │ │ AI & News      │
│  Engine      │ │ (AMFI/MF)  │ │ (Nemotron via  │
│ (20 tests)   │ │            │ │  Nebius +      │
│              │ │            │ │  Tavily)       │
└──────┬───────┘ └─────┬──────┘ └───────┬────────┘
       │               │                │
       └───────────────┼────────────────┘
                       ▼
            ┌────────────────────┐
            │   SQLite DB (db.py)│
            │  Profiles, Goals,  │
            │  Audited Portfolios│
            └────────────────────┘
```

---

## ✨ Standout Features

- **Advanced Feature 1: Financial Safety Net Before Investing**  
  Calculates emergency gap and warns against equity investments before clearing high-interest debt.
- **Advanced Feature 2: Explainable Portfolio Simulator**  
  Compares Accessible vs. Balanced vs. Growth scenarios with deterministic downside stress cases (\(-35\%\) equity shock) and Nemotron risk trade-off explanations.
- **Advanced Feature 3: News Intelligence with Causality & Timestamp Verification**  
  Tavily integration with publication date reconciliation against market dates to prevent false causal attributions.
- **Advanced Feature 4: Regional-Language Financial Coach**  
  Conversational financial coach supporting **English**, **हिन्दी (Hindi)**, and **தமிழ் (Tamil)**.
- **Advanced Feature 5: AI Portfolio Health Monitor**  
  Herfindahl-Hirschman Index (**HHI**) concentration analysis, single-asset exposure checks, and automated Nemotron risk audit.
- **Persistence Layer**: Built-in SQLite database (`data/paisapath.db`) storing user financial snapshots, goals, and portfolio audits.

---

## 🚀 Quickstart Guide

### 1. Set Up Environment
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
pip install -r requirements-api.txt
```

### 2. Configure Credentials (`.env`)
Fill in your API keys in `.env`:
```env
NEBIUS_API_KEY=your_actual_nebius_key
NEBIUS_BASE_URL=https://api.tokenfactory.nebius.com/v1/
NEBIUS_MODEL=nvidia/Llama-3_1-Nemotron-Ultra-253B-v1

TAVILY_API_KEY=your_actual_tavily_key
```
*(Note: If keys are omitted, the application runs seamlessly in contextual Demo Fallback Mode without crashing).*

### 3. Run Automated Tests
```bash
python -m pytest
# 20 passed tests covering financial maths, AMFI parser, and API endpoints
```

---

## 🖥️ Running the Application

### Option A: Streamlit All-in-One Dashboard (Port 8501)
```bash
streamlit run app.py
```

### Option B: FastAPI + Modern React Frontend

**Terminal 1 — FastAPI Backend (Port 8000):**
```bash
uvicorn api:app --reload --port 8000
```

**Terminal 2 — React Frontend (Port 5173):**
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

### Option C: Docker / Nebius Cloud Deployment (Single Command)
```bash
docker compose up -d --build
```
- React Frontend + FastAPI API: `http://localhost:8000/`
- Streamlit Dashboard: `http://localhost:8501/`
- See [DEPLOYMENT_NEBIUS.md](DEPLOYMENT_NEBIUS.md) for step-by-step Nebius AI Cloud VM deployment.

---

## 🔒 Honesty & Compliance Rules

1. **AMFI NAVs** are clearly labelled as **"Latest published NAV"** (published periodically by AMFI India, not intraday live streaming ticks).
2. **Stock quotes** are explicitly labelled as **DEMO** data until an authorized broker API feed is attached.
3. The language model **explains** verified figures; it is **never** permitted to hallucinate market prices or perform financial arithmetic.

*Disclaimer: PaisaPath AI is designed for financial education and planning simulations. It does not provide personalized investment advice.*
