"""PaisaPath AI - Streamlit front end."""
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

import financial_engine as fe
import market_data as md
from ai_agent import ask_nemotron
from news_agent import search_news

load_dotenv()
DEMO = json.loads((Path(__file__).parent / "data" / "demo_data.json").read_text())

st.set_page_config(page_title="PaisaPath AI", page_icon="🧭", layout="wide")
st.markdown("""<style>
h1,h2,h3{letter-spacing:-0.01em;color:#12262B}
.hero{background:#0F6B6B;color:#fff;padding:1.6rem 1.8rem;border-radius:6px;margin-bottom:1rem}
.hero h1{color:#fff;margin:0}.hero p{margin:.3rem 0 0;color:#DCEFEA}
.note{border-left:4px solid #F2A93B;background:#FFF6E3;padding:.6rem .9rem;margin:.5rem 0}
</style>""", unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>PaisaPath AI</h1>'
            '<p>Your income. Your goals. Your financial future. Check what you can afford before you invest.</p></div>',
            unsafe_allow_html=True)

fmt = lambda x: f"₹{x:,.0f}"

# ---------------- Sidebar profile ----------------
with st.sidebar:
    st.header("Your money")
    persona = st.selectbox("Try a sample person", ["Custom"] + list(DEMO["personas"]))
    p = DEMO["personas"].get(persona, {"income": 25000, "expenses": 19000, "debt": 2000, "savings": 5000, "goal": 200000})
    income = st.number_input("Monthly take-home income (₹)", 0, 10_000_000, p["income"], 1000)
    expenses = st.number_input("Monthly household expenses (₹)", 0, 10_000_000, p["expenses"], 500)
    debt = st.number_input("Monthly loan repayments (₹)", 0, 10_000_000, p["debt"], 500)
    savings = st.number_input("Savings you have today (₹)", 0, 100_000_000, p["savings"], 1000)
    hi_debt = st.checkbox("I have credit-card or other high-interest debt")
    goal_amt = st.number_input("Goal amount (₹)", 1000, 1_000_000_000, p["goal"], 10_000)
    goal_years = st.slider("Years until you need the money", 1, 30, 3)
    risk = st.select_slider("If investments fell 20%, I would…",
                            ["sell everything", "feel very worried", "wait it out", "invest more"], "feel very worried")

cap = fe.savings_capacity(income, expenses, debt, savings, hi_debt)
months = goal_years * 12
context = {"profile": {"income": income, "expenses": expenses, "debt_payments": debt, "savings": savings,
                       "high_interest_debt": hi_debt, "reaction_to_20pct_fall": risk},
           "capacity": cap, "goal": {"amount": goal_amt, "months": months,
                                     "zero_return_monthly": fe.monthly_saving_needed(goal_amt, months, savings)},
           "note": "All projections are illustrative assumptions, not guarantees."}

tabs = st.tabs(["1 · Can I invest?", "2 · Goal planner", "3 · Portfolio simulator", "4 · Markets & news", "5 · Ask the coach"])

# ---------------- Tab 1 ----------------
with tabs[0]:
    c1, c2, c3 = st.columns(3)
    c1.metric("Monthly surplus", fmt(cap["surplus"]))
    c2.metric("Comfortable to save", f"{fmt(cap['suggested_low'])} – {fmt(cap['suggested_high'])}")
    c3.metric("Emergency cover", f"{cap['emergency_coverage_months']:.1f} / 6 months")
    st.progress(min(1.0, cap["emergency_coverage_months"] / 6), text="Emergency fund progress")
    if cap["safety_net_first"]:
        st.warning("Safety net first: build your emergency fund and clear costly debt before taking market risk.")
    else:
        st.success("Your safety net looks healthy. You can explore investing, but amounts and risk still depend on your goal.")
    for f in cap["flags"]:
        st.markdown(f"- {f}")
    st.caption("We suggest a range, not your whole surplus, so irregular expenses do not push you into debt.")

# ---------------- Tab 2 ----------------
with tabs[1]:
    st.subheader(f"Reach {fmt(goal_amt)} in {goal_years} years")
    rates = [0.0, 0.04, 0.07, 0.10]
    rows = fe.scenario_table(goal_amt, months, savings, rates)
    df = pd.DataFrame({"Assumed yearly return": [f"{r['assumed_annual_return']:.0%}" for r in rows],
                       "Monthly amount needed": [r["monthly_needed"] for r in rows],
                       "You put in": [r["total_contributed"] for r in rows]})
    st.dataframe(df.style.format({"Monthly amount needed": "₹{:,.0f}", "You put in": "₹{:,.0f}"}), hide_index=True)
    st.markdown('<div class="note">Higher assumed returns lower the monthly amount, but market returns are '
                'uncertain and can be negative. 0% is the no-risk-of-loss baseline.</div>', unsafe_allow_html=True)
    infl = st.slider("Assumed yearly inflation", 0.0, 12.0, 6.0, 0.5) / 100
    st.write(f"If this goal costs {fmt(goal_amt)} today, it may cost about "
             f"**{fmt(fe.inflation_adjusted_target(goal_amt, infl, goal_years))}** in {goal_years} years.")
    need = rows[0]["monthly_needed"]
    if cap["suggested_high"] and need > cap["suggested_high"]:
        st.error(f"The zero-return plan needs {fmt(need)} a month, above your comfortable range. "
                 "Consider a longer timeline or a smaller goal.")

# ---------------- Tab 3 ----------------
with tabs[2]:
    st.subheader("Compare three illustrative portfolios")
    st.caption("Percentages and returns are illustrative assumptions, not recommendations or forecasts.")
    monthly = st.number_input("Monthly contribution (₹)", 0, 1_000_000, int(max(cap["suggested_low"], 500)), 500)
    fee = st.slider("Yearly cost of funds (%)", 0.0, 3.0, 0.5, 0.1) / 100
    missed = st.slider("Months you miss contributing", 0, min(months, 24), 0)
    presets = {"A · Keep money accessible": (80, 20, 0), "B · Balanced": (30, 40, 30), "C · Growth-oriented": (10, 20, 70)}
    results, cols = [], st.columns(3)
    for col, (name, (c, d, e)) in zip(cols, presets.items()):
        with col:
            st.markdown(f"**{name}**")
            c_ = st.number_input("Cash %", 0, 100, c, key=f"c{name}")
            d_ = st.number_input("Debt funds %", 0, 100, d, key=f"d{name}")
            e_ = st.number_input("Equity %", 0, 100, e, key=f"e{name}")
            alloc = {"cash": c_, "debt": d_, "equity": e_}
            try:
                r = fe.project_scenario(monthly, months, alloc, savings, infl, fee, missed)
                results.append({"Scenario": name, **r})
                st.metric("Projected", fmt(r["projected"]))
                st.metric("Bad-year stress case", fmt(r["stress_case"]))
                st.caption(f"Today's-money value: {fmt(r['real_value'])}")
                if r["stress_below_invested"]:
                    st.warning("In the stress case you could end up with less than you put in.")
            except ValueError as ex:
                st.error(str(ex))
    if results:
        chart = pd.DataFrame(results).melt("Scenario", ["invested", "projected", "stress_case"])
        st.plotly_chart(px.bar(chart, x="Scenario", y="value", color="variable", barmode="group",
                               color_discrete_sequence=["#9AA9A6", "#0F6B6B", "#F2A93B"]), use_container_width=True)
        if st.button("Explain these scenarios (Nemotron)"):
            with st.spinner("Asking Nemotron…"):
                try:
                    st.write(ask_nemotron("Explain these three scenarios, their trade-offs and downside risk for this person's goal.",
                                          {**context, "scenarios": results}))
                except Exception as ex:
                    st.error(f"AI call failed: {ex}")

# ---------------- Tab 4 ----------------
with tabs[3]:
    left, right = st.columns(2)
    with left:
        st.subheader("Mutual fund NAV")
        q = st.text_input("Search a scheme", "nifty 50 index direct growth")
        if st.button("Search AMFI"):
            st.session_state["funds"] = md.search_amfi(q)
        res = st.session_state.get("funds")
        if res:
            if res.get("error"):
                st.error(res["error"])
            if res.get("stale"):
                st.warning("AMFI could not be reached. Showing an older saved copy.")
            fdf = pd.DataFrame(res["results"])
            if not fdf.empty:
                st.dataframe(fdf[["scheme_code", "scheme_name", "nav", "nav_date"]], hide_index=True)
                st.caption("Latest published NAV from AMFI India. NAVs are published periodically, not live.")
                code = st.selectbox("Pick a scheme", fdf["scheme_code"])
                if st.button("Show NAV history"):
                    try:
                        h = md.nav_history(code)
                        hdf = pd.DataFrame(h["history"])
                        st.plotly_chart(px.line(hdf, x="date", y="nav"), use_container_width=True)
                        if len(hdf) > 1:
                            ch = fe.pct_change(hdf.nav.iloc[-1], hdf.nav.iloc[-2])
                            st.session_state["fund_ctx"] = {"scheme": h["meta"].get("scheme_name"),
                                "latest_nav": hdf.nav.iloc[-1], "nav_date": str(hdf.date.iloc[-1].date()),
                                "change_vs_previous_nav_pct": round(ch, 2), "source": h["source"]}
                            st.metric("Change vs previous NAV", f"{ch:+.2f}%")
                    except Exception as ex:
                        st.error(f"Could not load history: {ex}")
    with right:
        st.subheader("Stock quote (demo mode)")
        st.markdown('<div class="note">Demo data. Connect a licensed market-data provider in <code>market_data.py</code> for real quotes.</div>',
                    unsafe_allow_html=True)
        sym = st.selectbox("Symbol", [s["symbol"] for s in DEMO["demo_stocks"]])
        quote = md.get_stock_quote(sym)
        st.metric(quote["name"], f"₹{quote['price']:,.2f}", f"{quote['change_percent']:+.2f}%")
        st.caption(f"{quote['source']} · {quote['session']} · fetched {quote['retrieved_at']}")

    st.divider()
    st.subheader("News check")
    topic = st.text_input("Topic, company or fund", "Nifty 50")
    if st.button("Search news and explain"):
        try:
            news = search_news(topic)
            st.session_state["news"] = news
        except Exception as ex:
            st.error(f"News search failed: {ex}")
    news = st.session_state.get("news")
    if news:
        if news.get("error"):
            st.error(news["error"])
        for n in news["results"]:
            st.markdown(f"- [{n['title']}]({n['url']}) ({n['published'] or 'date unknown'})")
        if news["results"] and st.button("Explain what this means (Nemotron)"):
            with st.spinner("Asking Nemotron…"):
                try:
                    st.write(ask_nemotron(f"What do these news items say about {topic}? Do they explain recent price moves? Say what cannot be established.",
                                          {"news": news["results"], "market": st.session_state.get("fund_ctx")}))
                except Exception as ex:
                    st.error(f"AI call failed: {ex}")

# ---------------- Tab 5 ----------------
with tabs[4]:
    st.subheader("Ask in simple words")
    lang = st.radio("Language", ["English", "Hindi"], horizontal=True)
    st.caption("Try: What is an SIP? · Can I lose money in a mutual fund? · FD or debt fund?")
    st.session_state.setdefault("chat", [])
    for m in st.session_state["chat"]:
        st.chat_message(m["role"]).write(m["content"])
    if prompt := st.chat_input("Ask a money question"):
        st.chat_message("user").write(prompt)
        try:
            ans = ask_nemotron(prompt + (" Reply in Hindi." if lang == "Hindi" else ""), context,
                               st.session_state["chat"])
        except Exception as ex:
            ans = f"The AI service is unavailable: {ex}"
        st.chat_message("assistant").write(ans)
        st.session_state["chat"] += [{"role": "user", "content": prompt}, {"role": "assistant", "content": ans}]

st.caption("PaisaPath AI is for education. It is not investment advice. Market-linked returns are not guaranteed.")
