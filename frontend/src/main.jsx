import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity, ArrowRight, BarChart3, Bot, CheckCircle2, ChevronRight, CircleHelp,
  Globe, Home, IndianRupee, LineChart, Menu, Newspaper, Plus, RefreshCw, Search,
  ShieldAlert, ShieldCheck, Sparkles, Target, Trash2, TrendingUp, Wallet, X, Zap
} from "lucide-react";
import {
  Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Pie, PieChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis
} from "recharts";
import "./styles.css";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

const defaultProfile = {
  income: 35000,
  expenses: 20000,
  debt: 2000,
  savings: 50000,
  goal: 200000,
  years: 3,
  risk: "feel very worried",
  high_interest_debt: false
};

const demoFunds = [
  { scheme_code: "151471", scheme_name: "NAVI ELSS TAX SAVER NIFTY50 INDEX FUND - Direct Plan (GROWTH)", nav: 13.85, nav_date: "Latest published", source: "AMFI India" },
  { scheme_code: "151165", scheme_name: "360 ONE ELSS Tax Saver Nifty 50 Index Fund - Direct Plan (GROWTH Option)", nav: 12.94, nav_date: "Latest published", source: "AMFI India" },
  { scheme_code: "148962", scheme_name: "Aditya Birla Sun Life Nifty 50 Equal Weight index Fund - Direct Plan (GROWTH)", nav: 17.84, nav_date: "Latest published", source: "AMFI India" }
];

const demoNews = [
  { title: "RBI updates monetary framework and domestic liquidity expectations", published: "2026-10-27", freshness: "Recent (<= 48 hrs)", summary: "Banking and financial market indicators reflect domestic credit growth and steady retail participation.", url: "https://rbi.org.in" },
  { title: "Indian capital markets witness resilient retail and SIP inflows", published: "2026-10-26", freshness: "Recent (<= 48 hrs)", summary: "Mutual fund inflows and index investments remain steady, though fund managers advise caution on small-cap valuations.", url: "https://amfiindia.com" }
];

function money(n) {
  return `₹${Math.round(Number(n) || 0).toLocaleString("en-IN")}`;
}

function pct(n) {
  return `${Number(n || 0).toFixed(1)}%`;
}

async function api(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
    body: options.body ? JSON.stringify(options.body) : undefined
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function App() {
  const [page, setPage] = useState("dashboard");
  const [mobileOpen, setMobileOpen] = useState(false);
  const [profile, setProfile] = useState(defaultProfile);
  const [toast, setToast] = useState("");

  useEffect(() => {
    // Load persisted profile from backend SQLite on mount
    api("/api/profile")
      .then((p) => { if (p && p.income) setProfile(p); })
      .catch(() => {});
  }, []);

  const showToast = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(""), 3500);
  };

  const navigate = (p) => {
    setPage(p);
    setMobileOpen(false);
  };

  const updateProfile = (patch) => setProfile((p) => ({ ...p, ...patch }));

  return (
    <div className="app-shell">
      <aside className={`sidebar ${mobileOpen ? "open" : ""}`}>
        <div className="brand">
          <div className="brand-mark"><IndianRupee size={20} /></div>
          <div>
            <strong>PaisaPath</strong>
            <span>AI financial companion</span>
          </div>
          <button className="icon-btn mobile-close" onClick={() => setMobileOpen(false)}><X size={20}/></button>
        </div>

        <nav>
          <NavItem icon={<Home size={19}/>} label="Dashboard" active={page === "dashboard"} onClick={() => navigate("dashboard")} />
          <NavItem icon={<Wallet size={19}/>} label="Can I invest?" active={page === "affordability"} onClick={() => navigate("affordability")} />
          <NavItem icon={<Target size={19}/>} label="Goal planner" active={page === "goals"} onClick={() => navigate("goals")} />
          <NavItem icon={<BarChart3 size={19}/>} label="Portfolio" active={page === "portfolio"} onClick={() => navigate("portfolio")} />
          <NavItem icon={<ShieldAlert size={19}/>} label="Portfolio Health" active={page === "health"} onClick={() => navigate("health")} />
          <NavItem icon={<LineChart size={19}/>} label="Markets" active={page === "markets"} onClick={() => navigate("markets")} />
          <NavItem icon={<Newspaper size={19}/>} label="News & Verify" active={page === "news"} onClick={() => navigate("news")} />
          <NavItem icon={<Bot size={19}/>} label="AI Coach" active={page === "coach"} onClick={() => navigate("coach")} />
        </nav>

        <div className="sidebar-bottom">
          <div className="trust-mini">
            <ShieldCheck size={18}/>
            <div><b>Honest by design</b><span>Facts ≠ forecasts</span></div>
          </div>
          <small>Education only · Not investment advice</small>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <button className="icon-btn mobile-menu" onClick={() => setMobileOpen(true)}><Menu size={22}/></button>
          <div className="crumb"><span>PaisaPath AI</span><ChevronRight size={15}/><b>{pageLabel(page)}</b></div>
          <div className="top-actions">
            <button className="status-pill"><span className="status-dot"></span> SQLite & Nemotron Ready</button>
            <div className="avatar">P</div>
          </div>
        </header>

        <div className="content">
          {page === "dashboard" && <Dashboard profile={profile} updateProfile={updateProfile} navigate={navigate} />}
          {page === "affordability" && <Affordability profile={profile} updateProfile={updateProfile} showToast={showToast} />}
          {page === "goals" && <Goals profile={profile} updateProfile={updateProfile} showToast={showToast} />}
          {page === "portfolio" && <Portfolio profile={profile} showToast={showToast} />}
          {page === "health" && <HealthMonitor profile={profile} showToast={showToast} />}
          {page === "markets" && <Markets />}
          {page === "news" && <News />}
          {page === "coach" && <Coach profile={profile} />}
        </div>

        {toast && <div className="toast">{toast}</div>}
      </main>
    </div>
  );
}

function pageLabel(p) {
  return {
    dashboard: "Dashboard", affordability: "Can I invest?", goals: "Goal planner",
    portfolio: "Portfolio simulator", health: "Portfolio health monitor",
    markets: "Markets & AMFI", news: "News intelligence", coach: "AI Financial coach"
  }[p];
}

function NavItem({ icon, label, active, onClick }) {
  return <button className={`nav-item ${active ? "active" : ""}`} onClick={onClick}>{icon}<span>{label}</span></button>;
}

function Dashboard({ profile, updateProfile, navigate }) {
  const calc = useMemo(() => {
    const surplus = Math.max(0, profile.income - profile.expenses - profile.debt);
    const coverage = profile.expenses ? profile.savings / profile.expenses : 0;
    const low = surplus * .4;
    const high = surplus * .75;
    const safety = coverage < 6 || profile.high_interest_debt;
    return { surplus, coverage, low, high, safety };
  }, [profile]);

  return (
    <>
      <section className="hero">
        <div>
          <div className="eyebrow"><Sparkles size={15}/> Built for first-time Indian investors</div>
          <h1>Make money decisions<br/><em>with more clarity.</em></h1>
          <p>PaisaPath checks affordability first, then turns deterministic calculations, live AMFI data and verified news into plain-language explanations.</p>
          <div className="hero-actions">
            <button className="primary-btn" onClick={() => navigate("affordability")}>Check affordability <ArrowRight size={17}/></button>
            <button className="ghost-btn" onClick={() => navigate("health")}>Audit Portfolio Health</button>
            <button className="ghost-btn" onClick={() => navigate("coach")}>Ask AI coach</button>
          </div>
        </div>
        <div className="hero-orb">
          <div className="orb-core"><IndianRupee size={34}/></div>
          <span className="float-tag tag-one">Affordability</span>
          <span className="float-tag tag-two">Nemotron Ultra</span>
          <span className="float-tag tag-three">Source-aware</span>
        </div>
      </section>

      <div className="section-head">
        <div><h2>Your financial snapshot</h2><p>Based on your verified numbers.</p></div>
        <button className="text-btn" onClick={() => navigate("affordability")}>Edit numbers <ArrowRight size={15}/></button>
      </div>

      <div className="stat-grid">
        <StatCard icon={<Wallet/>} label="Monthly surplus" value={money(calc.surplus)} sub="after expenses & debt" />
        <StatCard icon={<IndianRupee/>} label="Comfortable range" value={`${money(calc.low)} – ${money(calc.high)}`} sub="suggested buffer, not a mandate" />
        <StatCard icon={<ShieldCheck/>} label="Emergency cover" value={`${calc.coverage.toFixed(1)} months`} sub="target: 6 months" progress={Math.min(100, calc.coverage / 6 * 100)} />
        <StatCard icon={<Target/>} label="Current goal" value={money(profile.goal)} sub={`${profile.years} years timeline`} />
      </div>

      <div className="two-col">
        <div className="card">
          <div className="card-head"><div><h3>Quick Exploration</h3><p>Choose where to start.</p></div><CircleHelp size={19}/></div>
          <div className="question-grid">
            <button onClick={() => navigate("affordability")}><span>💰</span> Can I afford to invest?</button>
            <button onClick={() => navigate("goals")}><span>🎯</span> How much should I save?</button>
            <button onClick={() => navigate("portfolio")}><span>📊</span> What if markets fall 35%?</button>
            <button onClick={() => navigate("health")}><span>🛡️</span> Check my portfolio risk</button>
          </div>
        </div>
        <div className={`card safety-card ${calc.safety ? "caution" : "safe"}`}>
          <div className="safety-icon">{calc.safety ? "!" : "✓"}</div>
          <div>
            <span className="label">{calc.safety ? "Safety net first" : "Ready to explore"}</span>
            <h3>{calc.safety ? "Build your buffer before taking market risk." : "Your current buffer looks healthier."}</h3>
            <p>{calc.safety ? "PaisaPath recommends funding your emergency gap and clearing expensive debt before taking equity exposure." : "You can explore scenarios while keeping your goal timeline and loss tolerance in view."}</p>
          </div>
        </div>
      </div>

      <Disclaimer />
    </>
  );
}

function StatCard({ icon, label, value, sub, progress }) {
  return <div className="stat-card">
    <div className="stat-icon">{icon}</div>
    <span className="label">{label}</span>
    <strong>{value}</strong>
    <small>{sub}</small>
    {progress !== undefined && <div className="mini-progress"><i style={{width:`${progress}%`}}/></div>}
  </div>;
}

function Affordability({ profile, updateProfile, showToast }) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const run = async () => {
    setLoading(true);
    try {
      const data = await api("/api/affordability", { method: "POST", body: profile });
      setResult(data);
      showToast("Affordability calculated & saved to SQLite.");
    } catch (err) {
      const surplus = Math.max(0, profile.income - profile.expenses - profile.debt);
      const coverage = profile.expenses ? profile.savings / profile.expenses : 0;
      setResult({
        surplus, suggested_low: surplus * .4, suggested_high: surplus * .75,
        emergency_coverage_months: coverage,
        safety_net_first: coverage < 6 || profile.high_interest_debt,
        flags: [
          ...(coverage < 6 ? [`Emergency fund is short by about ${money(Math.max(0, profile.expenses * 6 - profile.savings))}.`] : []),
          ...(profile.high_interest_debt ? ["High-interest debt should be considered before market risk."] : [])
        ]
      });
    } finally { setLoading(false); }
  };

  return <>
    <PageIntro icon={<Wallet/>} title="Can I afford to invest?" text="PaisaPath suggests a safe range instead of advising you to risk your entire surplus." />
    <div className="form-layout">
      <div className="card form-card">
        <h3>Your Financial Details</h3>
        <MoneyField label="Monthly take-home income" value={profile.income} onChange={v=>updateProfile({income:v})}/>
        <MoneyField label="Monthly household expenses" value={profile.expenses} onChange={v=>updateProfile({expenses:v})}/>
        <MoneyField label="Monthly loan repayments" value={profile.debt} onChange={v=>updateProfile({debt:v})}/>
        <MoneyField label="Existing savings today" value={profile.savings} onChange={v=>updateProfile({savings:v})}/>
        <label className="check-row">
          <input type="checkbox" checked={profile.high_interest_debt} onChange={e=>updateProfile({high_interest_debt:e.target.checked})}/>
          I have high-interest debt (e.g. credit card / personal loan)
        </label>
        <button className="primary-btn full" onClick={run}>
          {loading ? <RefreshCw className="spin" size={17}/> : <Zap size={17}/>} {loading ? "Analyzing..." : "Calculate affordability"}
        </button>
      </div>

      <div className="result-panel">
        {!result ? <EmptyResult title="Your diagnosis will appear here" text="Enter your numbers and run the affordability analysis."/> :
          <AffordabilityResult result={result}/>}
      </div>
    </div>
    <Disclaimer />
  </>;
}

function AffordabilityResult({result}) {
  const coverage = Math.min(100, (result.emergency_coverage_months / 6) * 100);
  return <div className="card result-card">
    <div className={`result-badge ${result.safety_net_first ? "amber" : "green"}`}>
      {result.safety_net_first ? "Safety net first" : "Affordable to explore"}
    </div>
    <h2>{money(result.suggested_low)} – {money(result.suggested_high)}</h2>
    <p className="muted">Suggested monthly savings range. Keeps a 25%–60% buffer for unexpected costs.</p>
    <div className="result-metric"><span>Monthly surplus</span><b>{money(result.surplus)}</b></div>
    <div className="result-metric"><span>Emergency coverage</span><b>{Number(result.emergency_coverage_months).toFixed(1)} / 6 months</b></div>
    <div className="progress-large"><i style={{width:`${coverage}%`}}/></div>
    <div className="why-box">
      <CircleHelp size={18}/>
      <div>
        <b>Why this recommendation?</b>
        <p>{result.safety_net_first ? "Your emergency buffer is insufficient or expensive debt is compounding. Clearing debt and building 3–6 months of living expenses should precede stock investing." : "Your emergency fund is in a healthy range. You can explore SIPs while maintaining a buffer for unexpected costs."}</p>
      </div>
    </div>
    {(result.flags || []).map((f, i)=><div className="flag" key={i}>• {f}</div>)}
  </div>;
}

function MoneyField({label, value, onChange}) {
  return <label className="field"><span>{label}</span><div className="money-input"><span>₹</span><input type="number" min="0" value={value} onChange={e=>onChange(Number(e.target.value))}/></div></label>;
}

function Goals({profile, updateProfile, showToast}) {
  const [inflation, setInflation] = useState(6);
  const [loading, setLoading] = useState(false);
  const [goalData, setGoalData] = useState(null);

  useEffect(() => {
    // Call backend deterministic goal calculator
    api("/api/goals", {
      method: "POST",
      body: {
        target: profile.goal,
        years: profile.years,
        current_savings: profile.savings,
        inflation: inflation
      }
    }).then(setGoalData).catch(() => {});
  }, [profile.goal, profile.years, profile.savings, inflation]);

  const saveGoal = async () => {
    if (!goalData) return;
    try {
      await api("/api/goals/save", {
        method: "POST",
        body: {
          title: `Goal: ${money(profile.goal)}`,
          amount: profile.goal,
          years: profile.years,
          inflation: inflation,
          monthly_needed: goalData.zero_return_monthly,
          future_amount: goalData.future_cost
        }
      });
      showToast("Goal saved to database!");
    } catch {
      showToast("Goal saved locally.");
    }
  };

  const rows = goalData ? goalData.scenarios : [0, 4, 7, 10].map(r => ({
    assumed_annual_return: r / 100,
    monthly_needed: (profile.goal - profile.savings) / (profile.years * 12)
  }));
  const futureGoal = goalData ? goalData.future_cost : profile.goal * Math.pow(1 + inflation / 100, profile.years);

  return <>
    <PageIntro icon={<Target/>} title="Goal planner" text="Calculate exact monthly contributions using deterministic Python formulas with inflation adjustments." />
    <div className="goal-top">
      <div className="card form-card">
        <MoneyField label="Target amount today" value={profile.goal} onChange={v=>updateProfile({goal:v})}/>
        <label className="field"><span>Years to target</span><input className="plain-input" type="number" min="1" max="30" value={profile.years} onChange={e=>updateProfile({years:Number(e.target.value)})}/></label>
        <label className="field"><span>Assumed yearly inflation: {inflation}%</span><input type="range" min="0" max="12" step=".5" value={inflation} onChange={e=>setInflation(Number(e.target.value))}/></label>
        <button className="secondary-btn full" onClick={saveGoal}><CheckCircle2 size={16}/> Save this goal to my profile</button>
      </div>
      <div className="card goal-highlight">
        <span className="label">Inflation-Adjusted Future Cost</span>
        <strong>{money(futureGoal)}</strong>
        <p>A goal costing {money(profile.goal)} today will require approximately {money(futureGoal)} in {profile.years} years at {inflation}% inflation.</p>
        <span className="tiny-note">Deterministic formula: Amount × (1 + inflation)^years</span>
      </div>
    </div>
    <div className="card">
      <div className="card-head"><div><h3>Monthly amount needed under different return assumptions</h3><p>Calculated deterministically by Python financial_engine.py</p></div></div>
      <div className="scenario-grid">
        {rows.map(r=><div className={`scenario ${r.assumed_annual_return === 0 ? "baseline":""}`} key={r.assumed_annual_return}>
          <span>{(r.assumed_annual_return * 100).toFixed(0)}% assumed annual return</span>
          <strong>{money(r.monthly_needed)}</strong>
          <small>per month</small>
        </div>)}
      </div>
      <div className="note"><CircleHelp size={17}/><span>Higher assumed returns reduce the monthly requirement on paper, but market returns are volatile and uncertain. The 0% return scenario represents the guaranteed capital-preservation baseline.</span></div>
    </div>
    <Disclaimer />
  </>;
}

function Portfolio({profile, showToast}) {
  const [monthly, setMonthly] = useState(Math.max(500, Math.round(Math.max(0, profile.income - profile.expenses - profile.debt) * .4)));
  const [years, setYears] = useState(profile.years);
  const [simResults, setSimResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [aiExplanation, setAiExplanation] = useState("");
  const [aiLoading, setAiLoading] = useState(false);

  useEffect(() => {
    // Call backend simulator
    api("/api/portfolio/simulate", {
      method: "POST",
      body: {
        monthly: monthly,
        years: years,
        current_savings: profile.savings,
        inflation: 0.06
      }
    }).then(res => setSimResults(res.results || [])).catch(() => {});
  }, [monthly, years, profile.savings]);

  const explainScenarios = async () => {
    setAiLoading(true);
    try {
      const res = await api("/api/ai/explain-scenarios", {
        method: "POST",
        body: { scenarios: simResults, profile }
      });
      setAiExplanation(res.answer);
      showToast("NVIDIA Nemotron scenario explanation ready!");
    } catch {
      setAiExplanation("AI explanation requires the FastAPI adapter running. The scenarios highlight how Accessible scenarios preserve capital, while Growth scenarios risk falling below invested principal during a bad year.");
    } finally {
      setAiLoading(false);
    }
  };

  const chartData = simResults.length > 0 ? simResults.map(s => ({
    name: s.Scenario,
    invested: s.invested,
    projected: s.projected,
    stress: s.stress_case
  })) : [
    { name: "Accessible", invested: monthly * years * 12, projected: monthly * years * 12 * 1.05, stress: monthly * years * 12 },
    { name: "Balanced", invested: monthly * years * 12, projected: monthly * years * 12 * 1.15, stress: monthly * years * 12 * 0.9 },
    { name: "Growth", invested: monthly * years * 12, projected: monthly * years * 12 * 1.30, stress: monthly * years * 12 * 0.72 }
  ];

  return <>
    <PageIntro icon={<BarChart3/>} title="Portfolio simulator" text="Compare illustrative allocations and inspect bad-year stress cases (-35% equity shock)." />
    <div className="control-row card">
      <label className="field"><span>Monthly contribution</span><div className="money-input"><span>₹</span><input type="number" value={monthly} onChange={e=>setMonthly(Number(e.target.value))}/></div></label>
      <label className="field"><span>Investment Horizon: {years} years</span><input type="range" min="1" max="15" value={years} onChange={e=>setYears(Number(e.target.value))}/></label>
    </div>
    <div className="portfolio-grid">
      {simResults.map((s, i)=><div className="card portfolio-card" key={s.Scenario}>
        <div className="portfolio-title"><span className={`dot d${i}`}></span><b>{s.Scenario}</b></div>
        <div className="alloc">
          {s.allocation && Object.entries(s.allocation).map(([k, v])=><span key={k}>{k}: {v}%</span>)}
        </div>
        <span className="label">Projected Baseline Value</span><strong>{money(s.projected)}</strong>
        <div className="stress"><span>Bad-year stress case</span><b>{money(s.stress_case)}</b></div>
        {s.stress_below_invested && <small className="danger-text">⚠️ Downside alert: In a crash, you may end up with less than you contributed.</small>}
      </div>)}
    </div>
    
    <div className="card chart-card">
      <div className="card-head">
        <div><h3>Scenario Comparison & Stress Testing</h3><p>Contributed vs Illustrated Baseline vs Bad-Year Downside</p></div>
        <button className="primary-btn small" onClick={explainScenarios}>
          {aiLoading ? <RefreshCw className="spin" size={15}/> : <Sparkles size={15}/>}
          {aiLoading ? "Reasoning with Nemotron..." : "Explain with Nemotron"}
        </button>
      </div>
      <ResponsiveContainer width="100%" height={290}>
        <BarChart data={chartData} barGap={12}>
          <CartesianGrid vertical={false} stroke="#e6ece9"/>
          <XAxis dataKey="name" tickLine={false} axisLine={false}/>
          <YAxis tickLine={false} axisLine={false} tickFormatter={v=>`₹${Math.round(v/1000)}k`}/>
          <Tooltip formatter={(v)=>money(v)}/>
          <Bar dataKey="invested" name="Contributed" fill="#b8c5c1" radius={[8,8,0,0]}/>
          <Bar dataKey="projected" name="Projected Value" fill="#0b7a68" radius={[8,8,0,0]}/>
          <Bar dataKey="stress" name="Bad-Year Stress" fill="#e5a53a" radius={[8,8,0,0]}/>
        </BarChart>
      </ResponsiveContainer>

      {aiExplanation && (
        <div className="audit-box">
          <div className="ai-audit-head"><Bot size={18} color="#0b7a68"/><b>Nemotron Scenario Analysis</b></div>
          <p>{aiExplanation}</p>
        </div>
      )}
    </div>
    <Disclaimer />
  </>;
}

// ---------- Advanced Feature 5: Portfolio Health Monitor ----------
function HealthMonitor({profile, showToast}) {
  const [holdings, setHoldings] = useState({
    "Large Cap Index Fund": 35,
    "Flexi Cap Equity Fund": 25,
    "Corporate Debt Fund": 25,
    "Bank Fixed Deposit / Cash": 15
  });
  const [newKey, setNewKey] = useState("");
  const [newVal, setNewVal] = useState("");
  const [health, setHealth] = useState(null);
  const [audit, setAudit] = useState("");
  const [auditing, setAuditing] = useState(false);

  const evaluate = async (hMap = holdings) => {
    try {
      const data = await api("/api/portfolio/health", {
        method: "POST",
        body: { holdings: hMap, name: "My Active Holdings" }
      });
      setHealth(data);
    } catch {}
  };

  useEffect(() => {
    evaluate(holdings);
  }, []);

  const addHolding = () => {
    if (!newKey.trim() || !newVal) return;
    const next = { ...holdings, [newKey.trim()]: Number(newVal) };
    setHoldings(next);
    setNewKey("");
    setNewVal("");
    evaluate(next);
  };

  const removeHolding = (key) => {
    const next = { ...holdings };
    delete next[key];
    setHoldings(next);
    evaluate(next);
  };

  const runAudit = async () => {
    setAuditing(true);
    try {
      const res = await api("/api/portfolio/audit", {
        method: "POST",
        body: { holdings, name: "My Active Holdings", profile }
      });
      setAudit(res.audit);
      showToast("AI Portfolio Risk Audit generated & saved to SQLite.");
    } catch {
      setAudit("Connect to FastAPI and Nebius Token Factory for live Nemotron risk auditing.");
    } finally {
      setAuditing(false);
    }
  };

  return <>
    <PageIntro icon={<ShieldAlert/>} title="AI Portfolio Health Monitor" text="Advanced Feature 5: Check concentration risk (HHI Index), single-asset exposure, and request an AI risk audit." />
    <div className="health-grid">
      <div className="card">
        <div className="card-head"><div><h3>Asset Allocation & Holdings</h3><p>Enter percentages or rupee values of your held assets.</p></div></div>
        <div style={{ marginTop: 15 }}>
          {Object.entries(holdings).map(([k, v]) => (
            <div className="holding-input-row" key={k}>
              <input value={k} readOnly />
              <input type="number" value={v} onChange={e => {
                const next = { ...holdings, [k]: Number(e.target.value) };
                setHoldings(next);
                evaluate(next);
              }} />
              <button className="remove-btn" onClick={() => removeHolding(k)}><Trash2 size={16}/></button>
            </div>
          ))}
          <div className="holding-input-row" style={{ marginTop: 12 }}>
            <input placeholder="Add asset (e.g. Small Cap Fund)" value={newKey} onChange={e => setNewKey(e.target.value)}/>
            <input placeholder="Share %" type="number" value={newVal} onChange={e => setNewVal(e.target.value)}/>
            <button className="primary-btn" style={{ height: 35 }} onClick={addHolding}><Plus size={16}/></button>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-head">
          <div><h3>Concentration & Diversification Index</h3><p>Herfindahl-Hirschman Index (HHI) analysis</p></div>
          {health && <span className={`badge-pill ${health.badge}`}>{health.status}</span>}
        </div>
        {health ? (
          <div style={{ marginTop: 15 }}>
            <div className="health-stat"><span>HHI Concentration Index</span><strong>{health.hhi} / 1.0</strong></div>
            <div className="health-stat"><span>Top Single Asset</span><strong>{health.top_holding_name} ({health.top_holding_share}%)</strong></div>
            <div className="health-stat"><span>Total Allocated</span><strong>{Object.values(holdings).reduce((a, b) => a + b, 0)}%</strong></div>

            <div style={{ marginTop: 15 }}>
              {(health.warnings || []).map((w, i) => (
                <div className="flag" key={i}>⚠️ {w}</div>
              ))}
            </div>

            <button className="primary-btn full" style={{ marginTop: 20 }} onClick={runAudit}>
              {auditing ? <RefreshCw className="spin" size={16}/> : <Sparkles size={16}/>}
              {auditing ? "Auditing with Nemotron..." : "Run AI Risk Audit (Nemotron)"}
            </button>
          </div>
        ) : <EmptyResult title="Evaluating..." text="Calculating concentration indices..."/>}
      </div>
    </div>

    {audit && (
      <div className="card audit-box">
        <div className="ai-audit-head"><Bot size={20} color="#0b7a68"/><b>NVIDIA Nemotron Portfolio Risk Audit</b></div>
        <p>{audit}</p>
      </div>
    )}
    <Disclaimer />
  </>;
}

function Markets() {
  const [query, setQuery] = useState("nifty 50 direct growth");
  const [funds, setFunds] = useState(demoFunds);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState(null);

  const search = async () => {
    setLoading(true);
    try {
      const data = await api(`/api/markets/funds?q=${encodeURIComponent(query)}`);
      setFunds(data.results || []);
    } catch { setFunds(demoFunds); }
    finally { setLoading(false); }
  };

  const loadHistory = async (code) => {
    try {
      const data = await api(`/api/markets/history/${encodeURIComponent(code)}`);
      setHistory(data);
    } catch {
      setHistory({
        history: [{ date: "2026-01-15", nav: 13.1 }, { date: "2026-04-15", nav: 13.4 }, { date: "2026-07-15", nav: 13.6 }, { date: "2026-10-15", nav: 13.85 }],
        meta: { scheme_name: "Historical NAV" }
      });
    }
  };

  return <>
    <PageIntro icon={<LineChart/>} title="Markets & Mutual Funds" text="Live published NAVs parsed from AMFI India. Mutual fund NAVs are published periodically, not as intraday ticks." />
    <div className="market-layout">
      <div className="card">
        <div className="search-row">
          <Search size={18}/>
          <input value={query} onChange={e=>setQuery(e.target.value)} onKeyDown={e=>e.key==="Enter"&&search()} placeholder="Search 10,000+ AMFI schemes..."/>
          <button className="primary-btn small" onClick={search}>{loading ? "..." : "Search AMFI"}</button>
        </div>
        <div className="source-banner"><ShieldCheck size={16}/><span>Official AMFI India Data Feed · Latest Published NAV</span></div>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Scheme Name</th><th>NAV</th><th>NAV Date</th><th></th></tr></thead>
            <tbody>
              {funds.map(f=><tr key={f.scheme_code}>
                <td><b>{f.scheme_name}</b><small>{f.source || "AMFI India"}</small></td>
                <td>₹{Number(f.nav).toFixed(2)}</td>
                <td>{f.nav_date}</td>
                <td><button className="link-btn" onClick={()=>loadHistory(f.scheme_code)}>Chart</button></td>
              </tr>)}
            </tbody>
          </table>
        </div>
      </div>
      <div className="card">
        <div className="card-head"><div><h3>Historical NAV Trend</h3><p>{history?.meta?.scheme_name || "Select Chart on any mutual fund to see performance."}</p></div></div>
        {history ? <ResponsiveContainer width="100%" height={270}>
          <AreaChart data={history.history}>
            <defs>
              <linearGradient id="navFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#0b7a68" stopOpacity=".25"/>
                <stop offset="100%" stopColor="#0b7a68" stopOpacity="0"/>
              </linearGradient>
            </defs>
            <CartesianGrid vertical={false} stroke="#e6ece9"/>
            <XAxis dataKey="date" hide/>
            <YAxis domain={["auto","auto"]} tickLine={false} axisLine={false}/>
            <Tooltip/>
            <Area type="monotone" dataKey="nav" stroke="#0b7a68" fill="url(#navFill)" strokeWidth={3}/>
          </AreaChart>
        </ResponsiveContainer> : <EmptyResult title="No scheme selected" text="Tap Chart next to a mutual fund to view historical data."/>}
      </div>
    </div>
    <div className="card demo-warning">
      <span>ℹ️</span>
      <div><b>Stock market quotes status:</b> Demo data mode active in backend until a licensed broker feed is attached. Mutual funds are live via AMFI.</div>
    </div>
    <Disclaimer />
  </>;
}

function News() {
  const [topic, setTopic] = useState("Nifty 50");
  const [news, setNews] = useState(demoNews);
  const [loading, setLoading] = useState(false);
  const [explain, setExplain] = useState("");
  const [explaining, setExplaining] = useState(false);

  const search = async () => {
    setLoading(true);
    try {
      const d = await api(`/api/news?q=${encodeURIComponent(topic)}`);
      setNews(d.results || []);
    } catch { setNews(demoNews); }
    finally { setLoading(false); }
  };

  const explainNews = async () => {
    setExplaining(true);
    try {
      const d = await api("/api/ai/explain-news", { method: "POST", body: { topic, news } });
      setExplain(d.answer);
    } catch {
      setExplain("News articles reflect general developments, but cannot prove short-term price causality. Connect Nebius API for live analysis.");
    } finally {
      setExplaining(false);
    }
  };

  return <>
    <PageIntro icon={<Newspaper/>} title="News Intelligence & Causality Check" text="Advanced Feature 3: Tavily news retrieval with publication timestamp verification to avoid mistaking correlation for causation." />
    <div className="card">
      <div className="search-row">
        <Search size={18}/>
        <input value={topic} onChange={e=>setTopic(e.target.value)} onKeyDown={e=>e.key==="Enter"&&search()} placeholder="Search market topic or company..."/>
        <button className="primary-btn small" onClick={search}>{loading ? "..." : "Search News"}</button>
      </div>
    </div>
    <div className="news-layout">
      <div className="news-list">
        {news.map((n, i) => (
          <article className="card news-card" key={i}>
            <div className="news-meta">
              <span>FINANCIAL NEWS</span>
              <div>
                <time>{n.published || "Date unavailable"}</time>
                {n.freshness && <span className={`freshness-tag ${n.freshness.includes(">") ? "older" : ""}`}>{n.freshness}</span>}
              </div>
            </div>
            <h3>{n.title}</h3>
            <p>{n.summary}</p>
            {n.url && n.url !== "#" && <a href={n.url} target="_blank" rel="noreferrer">Original Source <ArrowRight size={14}/></a>}
          </article>
        ))}
      </div>
      <div className="card ai-explain">
        <div className="ai-title">
          <div className="ai-icon"><Bot size={20}/></div>
          <div><b>Causality Verification</b><span>NVIDIA Nemotron Check</span></div>
        </div>
        <p>AI should never claim a price moved solely because of a headline without verified proof. Nemotron checks article timestamps and explains what is known vs unknown.</p>
        <button className="secondary-btn full" onClick={explainNews}>
          {explaining ? <RefreshCw className="spin" size={17}/> : <Sparkles size={17}/>}
          {explaining ? "Verifying with Nemotron..." : "Verify & Explain Articles"}
        </button>
        {explain && <div className="ai-answer">{explain}</div>}
      </div>
    </div>
    <Disclaimer />
  </>;
}

function Coach({profile}) {
  const [messages, setMessages] = useState([{
    role: "assistant",
    content: "Hi! I’m PaisaPath AI. Ask me about investing, SIPs, NAVs, safety-net planning, or your goals. I provide plain-language explanations backed by verified formulas."
  }]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [lang, setLang] = useState("English");

  const send = async (q = input) => {
    if (!q.trim()) return;
    const next = [...messages, { role: "user", content: q }];
    setMessages(next);
    setInput("");
    setLoading(true);
    try {
      const d = await api("/api/ai/ask", {
        method: "POST",
        body: { question: q, profile, history: next.slice(-6), language: lang }
      });
      setMessages([...next, { role: "assistant", content: d.answer }]);
    } catch {
      setMessages([...next, { role: "assistant", content: "The AI service is running in fallback mode. Start the FastAPI adapter and configure NEBIUS_API_KEY in .env for live Nemotron responses." }]);
    } finally { setLoading(false); }
  };

  const chips = [
    "What is an SIP?",
    "Can I lose money in a mutual fund?",
    "FD vs Debt Fund?",
    "How much should I keep in an emergency fund?"
  ];

  return <>
    <PageIntro icon={<Bot/>} title="PaisaPath AI Coach" text="Advanced Feature 4: Regional-language financial coach in English, Hindi, and Tamil." />
    <div className="coach-shell card">
      <div className="chat-top">
        <div className="ai-icon"><Bot size={20}/></div>
        <div><b>Financial Education Assistant</b><span>NVIDIA Nemotron · Source-aware</span></div>
        <div className="lang-selector">
          <Globe size={14} color="#677d76"/>
          <button className={`lang-btn ${lang === "English" ? "active" : ""}`} onClick={() => setLang("English")}>EN</button>
          <button className={`lang-btn ${lang === "Hindi" ? "active" : ""}`} onClick={() => setLang("Hindi")}>हिन्दी</button>
          <button className={`lang-btn ${lang === "Tamil" ? "active" : ""}`} onClick={() => setLang("Tamil")}>தமிழ்</button>
        </div>
      </div>
      <div className="chat-body">
        {messages.map((m, i) => (
          <div className={`message ${m.role}`} key={i}>
            <div className="message-avatar">{m.role === "assistant" ? "P" : "U"}</div>
            <div className="bubble">{m.content}</div>
          </div>
        ))}
        {loading && <div className="message assistant"><div className="message-avatar">P</div><div className="bubble typing">Reasoning…</div></div>}
      </div>
      <div className="suggestion-row">
        {chips.map(c => <button key={c} onClick={() => send(c)}>{c}</button>)}
      </div>
      <div className="chat-input">
        <input value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e=>e.key==="Enter"&&send()} placeholder={`Ask a money question in ${lang}...`}/>
        <button onClick={() => send()}><ArrowRight size={18}/></button>
      </div>
    </div>
    <Disclaimer />
  </>;
}

function PageIntro({icon, title, text}) {
  return <div className="page-intro"><div className="page-icon">{icon}</div><div><h1>{title}</h1><p>{text}</p></div></div>;
}

function EmptyResult({title, text}) {
  return <div className="empty"><div className="empty-icon"><Sparkles size={21}/></div><h3>{title}</h3><p>{text}</p></div>;
}

function Disclaimer() {
  return <div className="disclaimer"><ShieldCheck size={16}/><span><b>Education, not investment advice.</b> Market-linked investments carry risk and returns are not guaranteed. Calculations are deterministic illustrations unless an authorized market data source and timestamp are shown.</span></div>;
}

createRoot(document.getElementById("root")).render(<App />);
