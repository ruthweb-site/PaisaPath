"""Explanation agent: NVIDIA Nemotron served through Nebius Token Factory.

Nebius exposes an OpenAI-compatible API, so we use the `openai` SDK with a custom base_url.
Confirm the base URL and exact model ID in your Nebius console, then set them in .env.
"""
from __future__ import annotations
import json
import os
from openai import OpenAI

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


def _client() -> OpenAI:
    key = os.getenv("NEBIUS_API_KEY")
    if not key:
        raise RuntimeError("NEBIUS_API_KEY is not set. Add it to .env")
    return OpenAI(base_url=os.getenv("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1/"),
                  api_key=key)


def ask_nemotron(question: str, context: dict | None = None, history: list[dict] | None = None) -> str:
    model = os.getenv("NEBIUS_MODEL", "nvidia/Llama-3_1-Nemotron-Ultra-253B-v1")
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    if context:
        msgs.append({"role": "system",
                     "content": "Verified facts and calculations (JSON):\n" + json.dumps(context, indent=2, default=str)})
    msgs += (history or [])[-6:]
    msgs.append({"role": "user", "content": question})
    resp = _client().chat.completions.create(model=model, messages=msgs, temperature=0.3, max_tokens=700)
    return resp.choices[0].message.content
