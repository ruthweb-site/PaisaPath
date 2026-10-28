import pytest
import market_data as md


def test_search_amfi_returns_results():
    res = md.search_amfi("nifty 50", limit=5)
    assert "results" in res
    assert len(res["results"]) > 0
    first = res["results"][0]
    assert first["nav"] > 0
    assert "scheme_name" in first
    assert "nav_date" in first
    assert first["source"] == "AMFI India"


def test_nav_history_resilience():
    # Even with non-existent code or network timeout, it must not throw an exception
    h = md.nav_history("123456")
    assert "history" in h
    assert len(h["history"]) > 0
    assert "nav" in h["history"][0]


def test_demo_stock_quote():
    q = md.get_stock_quote("DEMOTECH")
    assert q["symbol"] == "DEMOTECH"
    assert q["price"] > 0
    assert q["is_demo"] is True

