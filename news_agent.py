"""Tavily news retrieval. The app makes a real runtime call to Tavily (hackathon bonus requirement)."""
from __future__ import annotations
import os
import requests

TAVILY_URL = "https://api.tavily.com/search"


def search_news(query: str, days: int = 14, max_results: int = 5) -> dict:
    key = os.getenv("TAVILY_API_KEY")
    if not key:
        return {"results": [], "error": "TAVILY_API_KEY is not set"}
    r = requests.post(TAVILY_URL, headers={"Authorization": f"Bearer {key}"}, timeout=20,
                      json={"query": f"{query} India market news", "topic": "news", "days": days,
                            "max_results": max_results, "search_depth": "basic"})
    r.raise_for_status()
    items = [{"title": x.get("title"), "url": x.get("url"), "published": x.get("published_date"),
              "summary": (x.get("content") or "")[:400]} for x in r.json().get("results", [])]
    return {"results": items, "query": query}
