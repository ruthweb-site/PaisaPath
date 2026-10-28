"""Tavily news retrieval with timestamp reconciliation and causality verification.
Hackathon bonus: Live runtime call to Tavily with source citing & date check.
"""
from __future__ import annotations
import os
from datetime import datetime, timezone
import requests

TAVILY_URL = "https://api.tavily.com/search"


def reconcile_news_timestamps(items: list[dict], market_date: str | None = None) -> list[dict]:
    """Check publication timestamps against current date to flag stale news and prevent false causal links."""
    now = datetime.now(timezone.utc)
    annotated = []
    for item in items:
        pub = item.get("published")
        freshness = "Date unverified"
        age_days = None
        if pub:
            try:
                pub_clean = pub.replace("Z", "+00:00")
                if "T" in pub_clean:
                    pub_dt = datetime.fromisoformat(pub_clean)
                else:
                    pub_dt = datetime.strptime(pub[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
                diff = (now - pub_dt).total_seconds() / 86400
                age_days = round(diff, 1)
                if diff <= 2:
                    freshness = "Recent (<= 48 hrs)"
                elif diff <= 7:
                    freshness = "Past week"
                else:
                    freshness = "Older news (> 7 days - check relevance)"
            except Exception:
                freshness = "Date format unverified"
        annotated.append({**item, "freshness": freshness, "age_days": age_days})
    return annotated


def search_news(query: str, days: int = 14, max_results: int = 5) -> dict:
    key = os.getenv("TAVILY_API_KEY", "").strip()
    if not key or key == "your_key_here":
        sample_items = [
            {
                "title": f"RBI updates liquidity framework; steady retail capital flows in {query}",
                "url": "https://rbi.org.in",
                "published": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "summary": f"Banking indicators and financial market participation reflect stable domestic credit demand and disciplined retail investments in {query}.",
                "is_demo": True
            },
            {
                "title": f"Indian mutual fund industry reports record SIP inflows despite global volatility",
                "url": "https://amfiindia.com",
                "published": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "summary": f"Domestic institutional and retail SIP accounts sustained regular inflows across diversified index and hybrid portfolios related to {query}.",
                "is_demo": True
            }
        ]
        return {
            "results": reconcile_news_timestamps(sample_items),
            "query": query,
            "note": "Demo news data. Add TAVILY_API_KEY in .env for live Tavily searches.",
            "is_demo": True
        }
    try:
        r = requests.post(TAVILY_URL, headers={"Authorization": f"Bearer {key}"}, timeout=15,
                          json={"query": f"{query} India market news", "topic": "news", "days": days,
                                "max_results": max_results, "search_depth": "basic"})
        r.raise_for_status()
        raw_items = [{"title": x.get("title"), "url": x.get("url"), "published": x.get("published_date"),
                      "summary": (x.get("content") or "")[:400]} for x in r.json().get("results", [])]
        return {
            "results": reconcile_news_timestamps(raw_items),
            "query": query,
            "is_demo": False
        }
    except Exception as exc:
        return {"results": [], "error": f"Tavily search failed: {exc}", "query": query}
