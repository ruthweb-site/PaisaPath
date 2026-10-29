"""Explanation agent: NVIDIA Nemotron served through Nebius Token Factory.

Nebius exposes an OpenAI-compatible API, so we use the `openai` SDK with a custom base_url.
Confirm the base URL and exact model ID in your Nebius console, then set them in .env.
"""
from __future__ import annotations
import json
import logging
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are PaisaPath AI, a financial education assistant for first-time investors in India.
Rules:
- Explain in simple language. If asked for Hindi, reply in Hindi.
- Use ONLY the supplied JSON facts, calculations and news. Never invent prices, NAVs, returns or news.
- Separate facts, assumptions and unknowns. State the data timestamp and source when you cite a number.
- Never present a delayed quote or yesterday's NAV as live. Mutual fund NAVs are published periodically.
- Do not promise returns or predict prices. Explain downside risk and liquidity.
- If news and price data do not prove a cause, say the cause cannot be established.
- Do not tell the user to buy or sell a specific security. Explain trade-offs and list questions
  they should answer first (emergency fund, debt, time horizon, risk comfort).
- If emergency savings or high-interest debt are a concern, say so before discussing investing.
- Keep answers under 250 words unless asked for more."""


def _client() -> OpenAI | None:
    key = os.getenv("NEBIUS_API_KEY", "").strip()
    if not key or key == "your_key_here":
        return None
    base_url = os.getenv("NEBIUS_BASE_URL", "https://integrate.api.nvidia.com/v1/").rstrip("/") + "/"
    return OpenAI(base_url=base_url, api_key=key)


def _generate_fallback(question: str, context: dict | None = None, is_hindi: bool = False) -> str:
    """Contextual, deterministic fallback when Nebius API key is not configured or network fails."""
    ctx = context or {}
    cap = ctx.get("capacity", {})
    scenarios = ctx.get("scenarios", [])
    news = ctx.get("news", [])

    if is_hindi:
        if cap.get("safety_net_first"):
            return (
                "🔍 [डेमो मोड - नेबियस एपीआई कुंजी कॉन्फ़िगर करें]\n\n"
                "आपके आंकड़ों के अनुसार, आपके पास आपातकालीन फंड (Emergency Fund) की कमी है या उच्च ब्याज वाला कर्ज है। "
                "शेयर बाजार में निवेश करने से पहले कम से कम 3 से 6 महीने के खर्चों का सुरक्षा फंड बनाना बहुत जरूरी है, "
                "ताकि किसी भी अप्रत्याशित जरूरत के समय आपको नुकसान में निवेश न बेचना पड़े।"
            )
        return (
            "🔍 [डेमो मोड - नेबियस एपीआई कुंजी कॉन्फ़िगर करें]\n\n"
            "एसआईपी (SIP) का मतलब है हर महीने एक निश्चित राशि का अनुशासित निवेश। यह बाजार के उतार-चढ़ाव को संतुलित करता है। "
            "ध्यान रखें कि म्यूचुअल फंड या शेयर बाजार में रिटर्न की कोई गारंटी नहीं होती है और यह आपके जोखिम उठाने की क्षमता पर निर्भर करता है।"
        )

    # Check if explaining scenarios
    if scenarios:
        accessible = next((s for s in scenarios if "Accessible" in s.get("Scenario", "")), scenarios[0] if scenarios else {})
        growth = next((s for s in scenarios if "Growth" in s.get("Scenario", "")), scenarios[-1] if scenarios else {})
        return (
            "💡 **Scenario Analysis (Demo Mode — Add NEBIUS_API_KEY in .env for live Nemotron reasoning)**\n\n"
            f"1. **{accessible.get('Scenario', 'Accessible Scenario')}**: Prioritizes capital preservation and liquidity. "
            f"In a severe market downturn, the downside shock is minimal (stress value ~₹{accessible.get('stress_case', 0):,.0f}), "
            "making it suitable for goals within 1–3 years or for individuals without an emergency cushion.\n\n"
            f"2. **{growth.get('Scenario', 'Growth Scenario')}**: Offers higher illustrative upside (~₹{growth.get('projected', 0):,.0f}) "
            f"over longer horizons, but exposes you to severe short-term declines (bad-year stress ~₹{growth.get('stress_case', 0):,.0f}). "
            "Notice that in a market crash, your value can fall below what you contributed.\n\n"
            "**Key Rule**: If you need this money within 3 years, avoid high equity exposure. "
            "Ensure your 6-month emergency buffer is funded before committing to growth portfolios."
        )

    # Check if explaining news
    if news:
        titles = [n.get("title", "") for n in news[:2] if n.get("title")]
        titles_summary = f" (e.g. '{titles[0]}')" if titles else ""
        return (
            "📰 **Market & News Context (Demo Mode — Add NEBIUS_API_KEY in .env for live Nemotron reasoning)**\n\n"
            f"The retrieved articles{titles_summary} discuss recent market movements and economic indicators. "
            "**Important Caution**: Available news articles describe events, but they **cannot establish a direct cause** "
            "for immediate stock price or NAV fluctuations. Short-term movements reflect broad market liquidity, global interest "
            "rates, and investor sentiment rather than any single headline. Avoid trading based purely on news."
        )

    # General coaching
    q_lower = question.lower()
    if "sip" in q_lower:
        return (
            "💡 **What is an SIP? (Demo Mode — Add NEBIUS_API_KEY in .env for live Nemotron reasoning)**\n\n"
            "An **SIP (Systematic Investment Plan)** is simply a method of investing a fixed sum of money periodically "
            "(e.g., monthly) into a mutual fund.\n\n"
            "- It is **not** a separate asset class or a guaranteed return product.\n"
            "- It helps with **rupee-cost averaging**: you buy more units when markets are low and fewer when markets are high.\n"
            "- It does **not** guarantee returns. The underlying fund value can still fall during market corrections."
        )
    elif "lose money" in q_lower or "risk" in q_lower:
        return (
            "⚠️ **Can you lose money in mutual funds? (Demo Mode — Add NEBIUS_API_KEY in .env for live Nemotron reasoning)**\n\n"
            "**Yes.** Mutual fund investments are subject to market risks. Unlike a bank fixed deposit, mutual funds have no government or capital guarantees.\n\n"
            "- **Equity funds**: Can fall 20% to 40% in a bad year.\n"
            "- **Debt funds**: Lower volatility, but they carry interest rate risk and credit risk.\n"
            "- **Rule of thumb**: Never invest money in equities if you need it within 3 years."
        )
    elif "emergency" in q_lower or "buffer" in q_lower or cap.get("safety_net_first"):
        surplus = cap.get("surplus", 0)
        gap = cap.get("emergency_gap", 0)
        return (
            f"🛡️ **Safety Net First (Demo Mode — Add NEBIUS_API_KEY in .env for live Nemotron reasoning)**\n\n"
            f"Based on your profile, your monthly surplus is approximately ₹{surplus:,.0f}, but your emergency fund "
            f"has an estimated gap of ₹{gap:,.0f}.\n\n"
            "Before investing in market-linked assets like stocks or mutual funds, you should build an accessible emergency "
            "cushion (held in a savings account or liquid fund) covering 3 to 6 months of living expenses. This protects you "
            "from having to sell investments at a loss when unexpected expenses occur."
        )
    else:
        return (
            "🧭 **Financial Guidance (Demo Mode — Add NEBIUS_API_KEY in .env for live Nemotron reasoning)**\n\n"
            f"Regarding your question: *'{question}'*\n\n"
            "As a beginner, remember the three fundamental rules of financial planning:\n"
            "1. **Safety First**: Clear high-interest credit card/personal loans and build a 6-month emergency reserve.\n"
            "2. **Goal & Horizon**: Match your investments to your timeline (short-term = bank deposits/liquid debt; long-term 5+ years = diversified index/equity funds).\n"
            "3. **Affordability**: Only invest what you can comfortably commit after accounting for household expenses and obligations."
        )


def ask_nemotron(question: str, context: dict | None = None, history: list[dict] | None = None) -> str:
    is_hindi = "hindi" in question.lower()
    client = _client()
    
    if client is None:
        return _generate_fallback(question, context, is_hindi)

    model = os.getenv("NEBIUS_MODEL", "nvidia/nemotron-3-ultra-550b-a55b")
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    if context:
        msgs.append({"role": "system",
                     "content": "Verified facts and calculations (JSON):\n" + json.dumps(context, indent=2, default=str)})
    msgs += (history or [])[-6:]
    msgs.append({"role": "user", "content": question})
    
    try:
        resp = client.chat.completions.create(model=model, messages=msgs, temperature=0.3, max_tokens=700)
        return resp.choices[0].message.content
    except Exception as exc:
        logger.warning(f"Nebius API call failed: {exc}. Using verified fallback.")
        return f"[Live Nebius call failed: {exc}]\n\n" + _generate_fallback(question, context, is_hindi)
