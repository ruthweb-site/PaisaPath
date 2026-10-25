import pytest
from financial_engine import *


def test_monthly_surplus():
    assert monthly_surplus(25000, 19000, 2000) == 4000
    assert monthly_surplus(10000, 12000, 0) == 0


def test_emergency_gap():
    assert emergency_fund_target(19000) == 114000
    assert emergency_gap(19000, 5000) == 109000
    assert emergency_gap(1000, 99999) == 0


def test_zero_return_goal():
    assert monthly_saving_needed(200000, 36) == pytest.approx(5555.56, abs=0.01)
    with pytest.raises(ValueError):
        monthly_saving_needed(1000, 0)


def test_sip_roundtrip():
    sip = required_sip(200000, 0.08, 36)
    assert future_value_sip(sip, 0.08, 36) == pytest.approx(200000, rel=1e-9)
    assert sip < monthly_saving_needed(200000, 36)


def test_sip_zero_rate():
    assert future_value_sip(1000, 0, 12) == 12000


def test_inflation():
    assert inflation_adjusted_target(100, 0.06, 1) == pytest.approx(106)
    assert real_value(106, 0.06, 1) == pytest.approx(100)


def test_capacity_flags_safety_net():
    c = savings_capacity(25000, 19000, 2000, 5000, has_high_interest_debt=True)
    assert c["surplus"] == 4000 and c["safety_net_first"]
    assert c["suggested_high"] < c["surplus"]


def test_allocation_validation():
    with pytest.raises(ValueError):
        blended_return({"cash": 50, "debt": 20, "equity": 20})


def test_scenario_orders_risk():
    safe = project_scenario(5000, 36, {"cash": 80, "debt": 20, "equity": 0})
    grow = project_scenario(5000, 36, {"cash": 10, "debt": 20, "equity": 70})
    assert grow["projected"] > safe["projected"]
    assert grow["stress_case"] < safe["stress_case"]


def test_missed_contributions_lower_value():
    a = {"cash": 20, "debt": 30, "equity": 50}
    assert project_scenario(5000, 36, a, missed_months=6)["projected"] < project_scenario(5000, 36, a)["projected"]


def test_concentration():
    assert concentration_hhi([1, 1, 1, 1]) == pytest.approx(0.25)
    assert top_holding_share({"A": 80, "B": 20}) == ("A", 80.0)


def test_pct_change_and_cagr():
    assert pct_change(110, 100) == pytest.approx(10)
    assert cagr(100, 121, 2) == pytest.approx(0.10)
