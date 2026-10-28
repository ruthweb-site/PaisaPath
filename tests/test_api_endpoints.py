import pytest
from fastapi.testclient import TestClient
import api

client = TestClient(api.app)


def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["ok"] is True


def test_affordability_and_profile():
    p = {
        "income": 35000,
        "expenses": 20000,
        "debt": 2000,
        "savings": 50000,
        "goal": 200000,
        "years": 3,
        "risk": "feel very worried",
        "high_interest_debt": False
    }
    res = client.post("/api/affordability", json=p)
    assert res.status_code == 200
    data = res.json()
    assert data["surplus"] == 13000
    assert data["suggested_low"] == 5200

    # Profile should be stored in SQLite
    prof_res = client.get("/api/profile")
    assert prof_res.status_code == 200
    assert prof_res.json()["income"] == 35000


def test_calculate_goals():
    res = client.post("/api/goals", json={
        "target": 200000,
        "years": 3,
        "current_savings": 50000,
        "inflation": 6.0
    })
    assert res.status_code == 200
    data = res.json()
    assert "scenarios" in data
    assert len(data["scenarios"]) == 4
    assert data["future_cost"] > 200000


def test_simulate_portfolio():
    res = client.post("/api/portfolio/simulate", json={
        "monthly": 5000,
        "years": 3,
        "current_savings": 50000,
        "inflation": 0.06
    })
    assert res.status_code == 200
    data = res.json()
    assert "results" in data
    assert len(data["results"]) == 3
    for r in data["results"]:
        assert "invested" in r
        assert "projected" in r
        assert "stress_case" in r


def test_portfolio_health_and_audit():
    holdings = {
        "Large Cap Index Fund": 40,
        "Tech Equity Fund": 30,
        "Corporate Debt": 20,
        "Bank Cash": 10
    }
    res = client.post("/api/portfolio/health", json={
        "holdings": holdings,
        "name": "Test Portfolio"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["hhi"] > 0
    assert data["top_holding_name"] == "Large Cap Index Fund"
    assert data["top_holding_share"] == 40.0
    assert "status" in data

    audit_res = client.post("/api/portfolio/audit", json={
        "holdings": holdings,
        "name": "Test Portfolio",
        "profile": {"income": 35000}
    })
    assert audit_res.status_code == 200
    assert "audit" in audit_res.json()

