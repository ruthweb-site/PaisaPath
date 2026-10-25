# PaisaPath AI
AI financial companion for first-time Indian investors. Checks affordability first, then explains goals,
scenarios, NAVs and news in plain language. Built for the Nebius x NVIDIA Global AI Hackathon.

## Architecture
Streamlit UI -> `financial_engine.py` (tested maths, no LLM) + `market_data.py` (AMFI NAV, stock provider)
+ `news_agent.py` (Tavily) -> `ai_agent.py` (NVIDIA Nemotron on Nebius Token Factory) explains verified results.

## Run
```bash
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env     # add NEBIUS_API_KEY, TAVILY_API_KEY; confirm model ID in Nebius console
pytest                   # 12 tests
streamlit run app.py
```

## Honesty rules
- AMFI NAVs are labelled "latest published NAV", never live.
- Stock quotes are DEMO until a licensed provider is wired into `get_stock_quote()`.
- Every number shows source and timestamp; the LLM never does arithmetic.

## Deploy (Nebius AI Cloud VM)
`streamlit run app.py --server.port 8501 --server.address 0.0.0.0`, set env vars, open the port.

## Not investment advice.
