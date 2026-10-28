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
        text = requests.get(AMFI_URL, timeout=10).text
        if "Scheme Code" in text and "Net Asset Value" in text:
            cache_file.write_text(text, encoding="utf-8")
    except Exception as exc:
        if not cache_file.exists():
            return {"results": [], "error": f"AMFI unreachable: {exc}", "stale": True}
        text, stale = cache_file.read_text(encoding="utf-8"), True
        retrieved = datetime.fromtimestamp(cache_file.stat().st_mtime, timezone.utc).isoformat(timespec="seconds")
    
    if not text and cache_file.exists():
        text, stale = cache_file.read_text(encoding="utf-8"), True

    q = query.lower().split()
    out = []
    for line in text.splitlines():
        p = line.split(";")
        # AMFI layout (8 columns):
        # 0: Scheme Code, 1: ISIN Payout, 2: ISIN Reinvest, 3: Scheme Name, 
        # 4: Plan (Direct/Regular), 5: Option (Growth/IDCW), 6: NAV, 7: Date
        if len(p) < 8 or not p[0].strip().isdigit():
            continue
        
        scheme_name = p[3].strip()
        plan = p[4].strip()
        option = p[5].strip()
        search_target = f"{scheme_name} {plan} {option}".lower()
        
        if all(w in search_target for w in q):
            try:
                nav = float(p[6].strip())
            except ValueError:
                continue
            
            display_name = f"{scheme_name} - {plan} ({option})" if plan and option else scheme_name
            out.append({
                "scheme_code": p[0].strip(),
                "scheme_name": display_name,
                "nav": nav,
                "nav_date": p[7].strip(),
                "source": "AMFI India",
                "retrieved_at": retrieved,
                "label": "Latest published NAV (not a live price)",
                "stale": stale
            })
            if len(out) >= limit:
                break
    return {"results": out, "stale": stale}


def nav_history(scheme_code: str) -> dict:
    """Historical NAV list [{date, nav}] oldest first, plus metadata.
    Includes caching and graceful fallback if mfapi.in times out or fails.
    """
    cache_file = CACHE / f"mf_{scheme_code}.json"
    
    # 1. Try to fetch live with short timeout
    try:
        r = requests.get(MFAPI.format(code=scheme_code), timeout=5)
        if r.status_code == 200:
            j = r.json()
            if j.get("data"):
                cache_file.write_text(json.dumps(j), encoding="utf-8")
                rows = [{"date": datetime.strptime(d["date"], "%d-%m-%Y"), "nav": float(d["nav"])} for d in j.get("data", [])]
                rows.sort(key=lambda x: x["date"])
                return {"meta": j.get("meta", {}), "history": rows, "source": "mfapi.in (mirrors AMFI)", "retrieved_at": _now()}
    except Exception:
        pass  # Fall through to cached or synthetic fallback

    # 2. Check local disk cache
    if cache_file.exists():
        try:
            j = json.loads(cache_file.read_text(encoding="utf-8"))
            rows = [{"date": datetime.strptime(d["date"], "%d-%m-%Y"), "nav": float(d["nav"])} for d in j.get("data", [])]
            rows.sort(key=lambda x: x["date"])
            return {"meta": j.get("meta", {}), "history": rows, "source": "Cached mfapi.in data", "retrieved_at": _now(), "cached": True}
        except Exception:
            pass

    # 3. Graceful synthetic fallback (ensures charts never crash)
    today = datetime.now(timezone.utc)
    base_nav = 50.0
    synth_rows = []
    for i in range(12, 0, -1):
        # 12 months history with modest realistic growth
        month_date = datetime(today.year - (1 if today.month <= i else 0), ((today.month - i - 1) % 12) + 1, 15)
        nav_val = round(base_nav * (1 + (12 - i) * 0.011), 2)
        synth_rows.append({"date": month_date, "nav": nav_val})
    
    return {
        "meta": {"scheme_code": scheme_code, "scheme_name": f"Scheme {scheme_code}"},
        "history": synth_rows,
        "source": "Sample NAV history (mfapi.in unavailable)",
        "retrieved_at": _now(),
        "is_fallback": True
    }


def get_stock_quote(symbol: str) -> dict:
    """TODO: replace with a licensed provider. Returns DEMO data flagged as such."""
    data = json.loads(DEMO.read_text())
    q = next((s for s in data["demo_stocks"] if s["symbol"].upper() == symbol.upper()), None)
    if not q:
        return {"error": f"No data for {symbol}"}
    return {**q, "is_demo": True, "is_delayed": True, "source": "Demo data (not a market feed)", "retrieved_at": _now()}
