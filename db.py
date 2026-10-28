"""SQLite persistence layer for PaisaPath AI.
Stores profiles, goals, portfolios, and scenario history so state survives page reloads.
"""
from __future__ import annotations
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).parent / "data" / "paisapath.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS profiles (
                id TEXT PRIMARY KEY,
                income REAL,
                expenses REAL,
                debt REAL,
                savings REAL,
                goal REAL,
                years INTEGER,
                risk TEXT,
                high_interest_debt INTEGER,
                updated_at TEXT
            );

            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id TEXT DEFAULT 'default',
                title TEXT,
                amount REAL,
                years INTEGER,
                inflation REAL,
                monthly_needed REAL,
                future_amount REAL,
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS portfolios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id TEXT DEFAULT 'default',
                name TEXT,
                holdings_json TEXT,
                hhi REAL,
                top_holding_name TEXT,
                top_holding_share REAL,
                ai_audit TEXT,
                updated_at TEXT
            );
        """)
        # Seed default profile if none exists
        cur = conn.cursor()
        cur.execute("SELECT id FROM profiles WHERE id = 'default'")
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO profiles (id, income, expenses, debt, savings, goal, years, risk, high_interest_debt, updated_at)
                VALUES ('default', 35000, 20000, 2000, 50000, 200000, 3, 'feel very worried', 0, ?)
            """, (_now(),))

        # Seed sample portfolio if none exists
        cur.execute("SELECT id FROM portfolios WHERE profile_id = 'default'")
        if not cur.fetchone():
            sample_holdings = {
                "Large Cap Index Fund": 35,
                "Flexi Cap Fund": 25,
                "Corporate Debt Fund": 25,
                "Bank Fixed Deposit / Cash": 15
            }
            cur.execute("""
                INSERT INTO portfolios (profile_id, name, holdings_json, hhi, top_holding_name, top_holding_share, ai_audit, updated_at)
                VALUES ('default', 'My Starter Portfolio', ?, 0.27, 'Large Cap Index Fund', 35.0, '', ?)
            """, (json.dumps(sample_holdings), _now()))
        conn.commit()


# Run initialization on import
init_db()


def get_profile(profile_id: str = "default") -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,)).fetchone()
        if not row:
            return None
        d = dict(row)
        d["high_interest_debt"] = bool(d["high_interest_debt"])
        return d


def save_profile(data: dict[str, Any], profile_id: str = "default") -> dict[str, Any]:
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO profiles (id, income, expenses, debt, savings, goal, years, risk, high_interest_debt, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                income=excluded.income,
                expenses=excluded.expenses,
                debt=excluded.debt,
                savings=excluded.savings,
                goal=excluded.goal,
                years=excluded.years,
                risk=excluded.risk,
                high_interest_debt=excluded.high_interest_debt,
                updated_at=excluded.updated_at
        """, (
            profile_id,
            float(data.get("income", 35000)),
            float(data.get("expenses", 20000)),
            float(data.get("debt", 2000)),
            float(data.get("savings", 50000)),
            float(data.get("goal", 200000)),
            int(data.get("years", 3)),
            str(data.get("risk", "feel very worried")),
            1 if data.get("high_interest_debt") else 0,
            _now()
        ))
        conn.commit()
    return get_profile(profile_id)


def list_goals(profile_id: str = "default") -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM goals WHERE profile_id = ? ORDER BY id DESC", (profile_id,)).fetchall()
        return [dict(r) for r in rows]


def save_goal(data: dict[str, Any], profile_id: str = "default") -> dict[str, Any]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO goals (profile_id, title, amount, years, inflation, monthly_needed, future_amount, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            profile_id,
            data.get("title", "My Financial Goal"),
            float(data.get("amount", 200000)),
            int(data.get("years", 3)),
            float(data.get("inflation", 6.0)),
            float(data.get("monthly_needed", 0.0)),
            float(data.get("future_amount", 0.0)),
            _now()
        ))
        conn.commit()
        goal_id = cur.lastrowid
        return dict(conn.execute("SELECT * FROM goals WHERE id = ?", (goal_id,)).fetchone())


def get_portfolio(profile_id: str = "default") -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM portfolios WHERE profile_id = ? ORDER BY id DESC LIMIT 1", (profile_id,)).fetchone()
        if not row:
            return None
        d = dict(row)
        try:
            d["holdings"] = json.loads(d["holdings_json"])
        except Exception:
            d["holdings"] = {}
        return d


def save_portfolio(data: dict[str, Any], profile_id: str = "default") -> dict[str, Any]:
    holdings = data.get("holdings", {})
    holdings_json = json.dumps(holdings)
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO portfolios (profile_id, name, holdings_json, hhi, top_holding_name, top_holding_share, ai_audit, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            profile_id,
            data.get("name", "Custom Portfolio"),
            holdings_json,
            float(data.get("hhi", 0.0)),
            data.get("top_holding_name", ""),
            float(data.get("top_holding_share", 0.0)),
            data.get("ai_audit", ""),
            _now()
        ))
        conn.commit()
    return get_portfolio(profile_id)

