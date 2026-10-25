"""Deterministic financial maths for PaisaPath AI.

Nothing in here calls an LLM. The language model only *explains* these numbers.
All projections are illustrative; market-linked returns are not guaranteed.
"""
from __future__ import annotations


# ---------- Cash-flow and safety net ----------
def monthly_surplus(income: float, expenses: float, debt_payments: float = 0) -> float:
    """Take-home income minus expenses and loan repayments (never below zero)."""
    return max(0.0, income - expenses - debt_payments)


def emergency_fund_target(monthly_expenses: float, months: int = 6) -> float:
    return monthly_expenses * months


def emergency_gap(monthly_expenses: float, current_savings: float, months: int = 6) -> float:
    return max(0.0, emergency_fund_target(monthly_expenses, months) - current_savings)


def emergency_coverage_months(monthly_expenses: float, current_savings: float) -> float:
    if monthly_expenses <= 0:
        return 0.0
    return current_savings / monthly_expenses


def savings_capacity(income, expenses, debt_payments, current_savings,
                     has_high_interest_debt=False, emergency_months=6) -> dict:
    """Return an *affordable range* (not a single instruction) plus plain-language flags."""
    surplus = monthly_surplus(income, expenses, debt_payments)
    gap = emergency_gap(expenses, current_savings, emergency_months)
    coverage = emergency_coverage_months(expenses, current_savings)
    flags = []
    # Keep a buffer: never plan to commit the entire surplus.
    low, high = surplus * 0.40, surplus * 0.75
    if surplus <= 0:
        flags.append("Your expenses and repayments use all of your income. Review costs before investing.")
        low = high = 0.0
    if gap > 0:
        flags.append(f"Emergency fund is short by about Rs {gap:,.0f} "
                     f"({coverage:.1f} of {emergency_months} months covered).")
    if has_high_interest_debt:
        flags.append("High-interest debt usually costs more than safe investments earn; "
                     "consider clearing it first.")
    safety_first = gap > 0 or has_high_interest_debt
    return {"surplus": surplus, "suggested_low": low, "suggested_high": high,
            "emergency_target": emergency_fund_target(expenses, emergency_months),
            "emergency_gap": gap, "emergency_coverage_months": coverage,
            "safety_net_first": safety_first, "flags": flags}


# ---------- Goal maths ----------
def monthly_saving_needed(target: float, months: int, current_savings: float = 0) -> float:
    """Zero-return contribution needed."""
    if months <= 0:
        raise ValueError("months must be greater than zero")
    return max(0.0, target - current_savings) / months


def future_value_sip(monthly: float, annual_rate: float, months: int, lump_sum: float = 0) -> float:
    """Value after `months` of end-of-month contributions at a constant assumed rate."""
    if months < 0:
        raise ValueError("months must be non-negative")
    r = annual_rate / 12
    if r == 0:
        return lump_sum + monthly * months
    growth = (1 + r) ** months
    return lump_sum * growth + monthly * (growth - 1) / r


def required_sip(target: float, annual_rate: float, months: int, current_savings: float = 0) -> float:
    """Monthly contribution needed to reach `target` at an assumed constant rate."""
    if months <= 0:
        raise ValueError("months must be greater than zero")
    r = annual_rate / 12
    if r == 0:
        return monthly_saving_needed(target, months, current_savings)
    growth = (1 + r) ** months
    remaining = max(0.0, target - current_savings * growth)
    return remaining * r / (growth - 1)


def inflation_adjusted_target(amount_today: float, inflation: float, years: float) -> float:
    """What a goal costing `amount_today` may cost in the future."""
    return amount_today * (1 + inflation) ** years


def real_value(nominal: float, inflation: float, years: float) -> float:
    """Purchasing power of a future amount in today's rupees."""
    return nominal / (1 + inflation) ** years


def scenario_table(target: float, months: int, current_savings: float, rates: list[float]) -> list[dict]:
    return [{"assumed_annual_return": r,
             "monthly_needed": required_sip(target, r, months, current_savings),
             "total_contributed": required_sip(target, r, months, current_savings) * months}
            for r in rates]


# ---------- Portfolio scenarios (illustrative assumptions, not forecasts) ----------
DEFAULT_ASSUMPTIONS = {
    #            assumed annual return, illustrative bad-year fall
    "cash":   {"return": 0.03, "shock": 0.00},
    "debt":   {"return": 0.06, "shock": -0.04},
    "equity": {"return": 0.11, "shock": -0.35},
}


def validate_allocation(alloc: dict) -> None:
    if any(v < 0 for v in alloc.values()):
        raise ValueError("allocations cannot be negative")
    if abs(sum(alloc.values()) - 100) > 0.01:
        raise ValueError("allocations must add up to 100")


def blended_return(alloc: dict, assumptions: dict = DEFAULT_ASSUMPTIONS, annual_fee: float = 0.0) -> float:
    validate_allocation(alloc)
    gross = sum(alloc[k] / 100 * assumptions[k]["return"] for k in alloc)
    return gross - annual_fee


def blended_shock(alloc: dict, assumptions: dict = DEFAULT_ASSUMPTIONS) -> float:
    validate_allocation(alloc)
    return sum(alloc[k] / 100 * assumptions[k]["shock"] for k in alloc)


def project_scenario(monthly: float, months: int, alloc: dict, lump_sum: float = 0,
                     inflation: float = 0.06, annual_fee: float = 0.0,
                     missed_months: int = 0, assumptions: dict = DEFAULT_ASSUMPTIONS) -> dict:
    """Projected value, a stress case (bad year just before the goal), and real value."""
    rate = blended_return(alloc, assumptions, annual_fee)
    paid_months = max(0, months - missed_months)
    # Missed contributions: simple approximation = fewer contributions, growth over full period.
    r = rate / 12
    growth = (1 + r) ** months
    value = lump_sum * growth
    if r == 0:
        value += monthly * paid_months
    else:
        value += monthly * ((1 + r) ** paid_months - 1) / r * (1 + r) ** (months - paid_months)
    stress = value * (1 + blended_shock(alloc, assumptions))
    invested = lump_sum + monthly * paid_months
    return {"assumed_return": rate, "invested": invested, "projected": value,
            "stress_case": stress, "real_value": real_value(value, inflation, months / 12),
            "stress_below_invested": stress < invested}


# ---------- Portfolio health ----------
def concentration_hhi(weights: list[float]) -> float:
    """Herfindahl index on 0-1 scale. Near 1 = concentrated."""
    total = sum(weights)
    if total <= 0:
        return 0.0
    return sum((w / total) ** 2 for w in weights)


def top_holding_share(holdings: dict[str, float]) -> tuple[str, float]:
    total = sum(holdings.values())
    if total <= 0:
        return ("", 0.0)
    name = max(holdings, key=holdings.get)
    return name, holdings[name] / total * 100


def pct_change(current: float, previous: float) -> float:
    if previous == 0:
        raise ValueError("previous value cannot be zero")
    return (current - previous) / previous * 100


def cagr(start: float, end: float, years: float) -> float:
    if start <= 0 or years <= 0:
        raise ValueError("start and years must be positive")
    return (end / start) ** (1 / years) - 1
