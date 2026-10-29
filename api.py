"""
PaisaPath FastAPI adapter.
Connects deterministic financial engine, market data, news intelligence,
persistence layer, and NVIDIA Nemotron AI agent to the frontend.
"""

from __future__ import annotations

from typing import Any
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import financial_engine as fe
import market_data as md
from ai_agent import ask_nemotron
from news_agent import search_news
import db

app = FastAPI(title="PaisaPath AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Pydantic Schemas ----------
class Profile(BaseModel):
    income: float = Field(35000, ge=0)
    expenses: float = Field(20000, ge=0)
    debt: float = Field(2000, ge=0)
    savings: float = Field(50000, ge=0)
    goal: float = Field(200000, ge=0)
    years: int = Field(3, ge=1, le=30)
    risk: str = "feel very worried"
    high_interest_debt: bool = False


class GoalsRequest(BaseModel):
    target: float = Field(..., gt=0)
    years: int = Field(..., ge=1, le=30)
    current_savings: float = Field(0, ge=0)
    inflation: float = Field(6.0, ge=0, le=25)
    rates: list[float] = [0.0, 0.04, 0.07, 0.10]


class PortfolioSimulateRequest(BaseModel):
    monthly: float = Field(..., ge=0)
    years: int = Field(..., ge=1, le=30)
    current_savings: float = Field(0, ge=0)
    inflation: float = Field(0.06, ge=0)
    annual_fee: float = Field(0.005, ge=0)
    missed_months: int = Field(0, ge=0)
    scenarios: dict[str, dict[str, float]] | None = None


class PortfolioHealthRequest(BaseModel):
    holdings: dict[str, float]  # e.g. {"Large Cap": 40, "Debt": 30, "Cash": 30}
    name: str = "My Portfolio"


class PortfolioAuditRequest(BaseModel):
    holdings: dict[str, float]
    name: str = "My Portfolio"
    profile: dict[str, Any] = {}


class AskRequest(BaseModel):
    question: str
    profile: dict[str, Any] = {}
    history: list[dict[str, str]] = []
    language: str = "English"


class NewsExplainRequest(BaseModel):
    topic: str
    news: list[dict[str, Any]] = []
    market_context: dict[str, Any] | None = None


# ---------- Endpoints ----------
@app.get("/api/health")
def health():
    return {"ok": True, "service": "PaisaPath AI API", "database": "SQLite ready"}


# 1. Profile & Affordability
@app.get("/api/profile")
def get_user_profile():
    p = db.get_profile("default")
    return p or Profile().model_dump()


@app.post("/api/profile")
def save_user_profile(p: Profile):
    return db.save_profile(p.model_dump(), "default")


@app.post("/api/affordability")
def affordability(p: Profile):
    cap = fe.savings_capacity(
        p.income,
        p.expenses,
        p.debt,
        p.savings,
        p.high_interest_debt,
    )
    # Persist updated profile numbers automatically
    db.save_profile(p.model_dump(), "default")
    return cap


# 2. Goal Planning
@app.post("/api/goals")
def calculate_goals(req: GoalsRequest):
    months = req.years * 12
    rates = req.rates or [0.0, 0.04, 0.07, 0.10]
    scenarios = fe.scenario_table(req.target, months, req.current_savings, rates)
    future_cost = fe.inflation_adjusted_target(req.target, req.inflation / 100, req.years)
    zero_need = fe.monthly_saving_needed(req.target, months, req.current_savings)
    
    return {
        "target": req.target,
        "years": req.years,
        "months": months,
        "inflation_rate": req.inflation,
        "future_cost": future_cost,
        "zero_return_monthly": zero_need,
        "scenarios": scenarios
    }


@app.get("/api/goals/saved")
def list_saved_goals():
    return db.list_goals("default")


@app.post("/api/goals/save")
def save_goal_record(req: dict[str, Any]):
    return db.save_goal(req, "default")


# 3. Portfolio Simulation & Health
@app.post("/api/portfolio/simulate")
def simulate_portfolio(req: PortfolioSimulateRequest):
    months = req.years * 12
    presets = req.scenarios or {
        "Accessible": {"cash": 80, "debt": 20, "equity": 0},
        "Balanced": {"cash": 30, "debt": 40, "equity": 30},
        "Growth-oriented": {"cash": 10, "debt": 20, "equity": 70}
    }
    
    results = []
    for name, alloc in presets.items():
        try:
            r = fe.project_scenario(
                req.monthly,
                months,
                alloc,
                req.current_savings,
                req.inflation,
                req.annual_fee,
                req.missed_months
            )
            results.append({
                "Scenario": name,
                "allocation": alloc,
                "invested": round(r["invested"]),
                "projected": round(r["projected"]),
                "stress_case": round(r["stress_case"]),
                "real_value": round(r["real_value"]),
                "assumed_return": round(r["assumed_return"], 4),
                "stress_below_invested": r["stress_below_invested"]
            })
        except ValueError as ex:
            results.append({"Scenario": name, "error": str(ex)})
            
    return {"results": results, "months": months}


@app.post("/api/portfolio/health")
def portfolio_health(req: PortfolioHealthRequest):
    holdings = req.holdings
    if not holdings:
        return {"error": "Holdings cannot be empty"}
    
    total = sum(holdings.values())
    if total <= 0:
        return {"error": "Total holding weight must be greater than zero"}
        
    weights = [v / total for v in holdings.values()]
    hhi = fe.concentration_hhi(weights)
    top_name, top_share = fe.top_holding_share(holdings)
    
    # Classification
    if hhi < 0.22:
        status = "Well Diversified"
        badge = "green"
    elif hhi <= 0.40:
        status = "Moderate Concentration"
        badge = "amber"
    else:
        status = "Highly Concentrated"
        badge = "red"
        
    warnings = []
    if top_share > 35:
        warnings.append(f"High single-asset exposure: '{top_name}' accounts for {top_share:.1f}% of total portfolio.")
    if hhi > 0.35:
        warnings.append("Concentration risk: Volatility in one asset will disproportionately affect portfolio value.")
    if not any("cash" in k.lower() or "deposit" in k.lower() or "liquid" in k.lower() for k in holdings):
        warnings.append("No immediate liquidity buffer detected inside portfolio assets.")
        
    return {
        "name": req.name,
        "holdings": holdings,
        "hhi": round(hhi, 3),
        "status": status,
        "badge": badge,
        "top_holding_name": top_name,
        "top_holding_share": round(top_share, 1),
        "warnings": warnings
    }


@app.post("/api/portfolio/audit")
def portfolio_audit(req: PortfolioAuditRequest):
    health_info = portfolio_health(PortfolioHealthRequest(holdings=req.holdings, name=req.name))
    question = (
        f"Audit this portfolio ({req.name}). "
        f"Top holding is {health_info.get('top_holding_name')} with {health_info.get('top_holding_share')}% share. "
        f"Herfindahl concentration index is {health_info.get('hhi')} ({health_info.get('status')}). "
        "Explain concentration risk, downside volatility, liquidity trade-offs, and recommend questions to consider."
    )
    context = {"portfolio_health": health_info, "profile": req.profile}
    audit_explanation = ask_nemotron(question, context)
    
    # Save to SQLite
    db.save_portfolio({
        "name": req.name,
        "holdings": req.holdings,
        "hhi": health_info.get("hhi", 0),
        "top_holding_name": health_info.get("top_holding_name", ""),
        "top_holding_share": health_info.get("top_holding_share", 0),
        "ai_audit": audit_explanation
    }, "default")
    
    return {
        "health": health_info,
        "audit": audit_explanation
    }


# 4. Markets & Stocks
@app.get("/api/markets/funds")
def funds(q: str = Query(..., min_length=1)):
    return md.search_amfi(q)


@app.get("/api/markets/history/{scheme_code}")
def fund_history(scheme_code: str):
    return md.nav_history(scheme_code)


@app.get("/api/stock/{symbol}")
def stock(symbol: str):
    return md.get_stock_quote(symbol)


# 5. News & AI Agents
@app.get("/api/news")
def news(q: str = Query(..., min_length=1)):
    return search_news(q)


@app.post("/api/ai/ask")
def ask(req: AskRequest):
    prompt_q = req.question
    if req.language.lower() == "hindi":
        prompt_q += " Reply in Hindi."
    elif req.language.lower() == "tamil":
        prompt_q += " Reply in Tamil."

    context = {
        "profile": req.profile,
        "capacity": fe.savings_capacity(
            req.profile.get("income", 0),
            req.profile.get("expenses", 0),
            req.profile.get("debt", 0),
            req.profile.get("savings", 0),
            req.profile.get("high_interest_debt", False),
        ),
        "note": "All projections are illustrative assumptions, not guarantees.",
    }
    return {"answer": ask_nemotron(prompt_q, context, req.history)}


@app.post("/api/ai/explain-news")
def explain_news(req: NewsExplainRequest):
    context = {"news": req.news, "topic": req.topic, "market": req.market_context}
    question = (
        f"What do these news items say about {req.topic}? "
        "Compare publication timestamps and state whether the news can causally prove recent price movements. "
        "Separate verified facts from unknowns."
    )
    return {"answer": ask_nemotron(question, context)}


@app.post("/api/ai/explain-scenarios")
def explain_scenarios(req: dict[str, Any]):
    scenarios = req.get("scenarios", [])
    profile = req.get("profile", {})
    context = {"scenarios": scenarios, "profile": profile}
    question = "Explain these three investment scenarios, their downside stress risk, and liquidity trade-offs for this investor."
    return {"answer": ask_nemotron(question, context)}


# 6. Serve built React Frontend SPA (Production Container & Cloud Deployment)
from pathlib import Path
from fastapi.staticfiles import StaticFiles

FRONTEND_DIST = Path(__file__).parent / "frontend" / "dist"
if FRONTEND_DIST.exists() and (FRONTEND_DIST / "index.html").exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")

