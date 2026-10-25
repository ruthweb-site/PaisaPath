"""Market data with honest labelling.

* Mutual funds: AMFI publishes NAVs periodically (not intraday). We label them "Latest published NAV".
* History: mfapi.in is a free community API mirroring AMFI data.
* Stocks: plug in a licensed provider (Upstox / Kite Connect / NSE agreement) in get_stock_quote().
  Until then the app uses clearly marked DEMO data. Never show demo data as live.
"""
from __future__ import annotations
import json
import time
from datetime import datetime, timezone
from pathlib import Path
import requests

AMFI_URL = "https://www.amfiindia.com/spages/NAVAll.txt"
MFAPI = "https://api.mfapi.in/mf/{code}"
CACHE = Path(__file__).parent / "data" / "cache"
CACHE.mkdir(parents=True, exist_ok=True)
DEMO = Path(__file__).parent / "data" / "demo_data.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def search_amfi(query: str, limit: int = 15) -> dict:
    """Search latest published NAVs. Falls back to cached file if AMFI is unreachable."""
    cache_file = CACHE / "navall.txt"
    stale, retrieved = False, _now()
    try:
        text = requests.get(AMFI_URL, timeout=15).text
        cache_file.write_text(text, encoding="utf-8")
    except Exception as exc:
        if not cache_file.exists():
            return {"results": [], "error": f"AMFI unreachable: {exc}", "stale": True}
        text, stale = cache_file.read_text(encoding="utf-8"), True
        retrieved = datetime.fromtimestamp(cache_file.stat().st_mtime, timezone.utc).isoformat(timespec="seconds")
    q, out = query.lower().split(), []
    for line in text.splitlines():
        p = line.split(";")
        if len(p) < 6 or not p[0].strip().isdigit():
            continue
        if all(w in p[3].lower() for w in q):
            try:
                nav = float(p[4])
            except ValueError:
                continue
            out.append({"scheme_code": p[0].strip(), "scheme_name": p[3].strip(), "nav": nav,
                        "nav_date": p[5].strip(), "source": "AMFI India", "retrieved_at": retrieved,
                        "label": "Latest published NAV (not a live price)", "stale": stale})
            if len(out) >= limit:
                break
    return {"results": out, "stale": stale}


def nav_history(scheme_code: str) -> dict:
    """Historical NAV list [{date, nav}] oldest first, plus metadata."""
    r = requests.get(MFAPI.format(code=scheme_code), timeout=20)
    r.raise_for_status()
    j = r.json()
    rows = [{"date": datetime.strptime(d["date"], "%d-%m-%Y"), "nav": float(d["nav"])} for d in j.get("data", [])]
    rows.sort(key=lambda x: x["date"])
    return {"meta": j.get("meta", {}), "history": rows, "source": "mfapi.in (mirrors AMFI)", "retrieved_at": _now()}


def get_stock_quote(symbol: str) -> dict:
    """TODO: replace with a licensed provider. Returns DEMO data flagged as such."""
    data = json.loads(DEMO.read_text())
    q = next((s for s in data["demo_stocks"] if s["symbol"].upper() == symbol.upper()), None)
    if not q:
        return {"error": f"No data for {symbol}"}
    return {**q, "is_demo": True, "is_delayed": True, "source": "Demo data (not a market feed)", "retrieved_at": _now()}
