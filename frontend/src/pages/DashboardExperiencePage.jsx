import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Cell, Legend, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import api from "../api/client";
import AlertPanel from "../components/AlertPanel";
import StatCard from "../components/StatCard";
import AppLayout from "../layouts/AppLayout";
import { formatCurrency, formatPercent } from "../utils/formatters";

const COLORS = ["#14b8a6", "#38bdf8", "#f59e0b", "#f87171", "#8b5cf6", "#22c55e"];

export default function DashboardExperiencePage() {
  const [summary, setSummary] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const quickActions = useMemo(
    () => [
      { title: "Add a transaction", description: "Log income or spending in a few seconds.", to: "/add-transaction" },
      { title: "Open planning", description: "Set monthly caps, goals, and recurring bills.", to: "/planning" },
      { title: "See recommendations", description: "Find overspending areas and next steps.", to: "/recommendations" },
    ],
    [],
  );

  const loadDashboard = async () => {
    setLoading(true);
    setError("");
    try {
      const [summaryRes, predictionRes, analysisRes] = await Promise.all([
        api.get("/finance/summary"),
        api.post("/ai/predict-expense", {}),
        api.post("/ai/analyze-spending", {}),
      ]);
      setSummary(summaryRes.data);
      setPrediction(predictionRes.data);
      setAnalysis(analysisRes.data);
    } catch {
      setError("Could not load the dashboard right now. Please refresh in a moment.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  if (loading && !summary) {
    return (
      <AppLayout title="Overview" subtitle="Loading your latest financial picture.">
        <div className="rounded-3xl border border-white/10 bg-slate-900/60 p-8 text-slate-300 shadow-soft">Loading dashboard...</div>
      </AppLayout>
    );
  }

  return (
    <AppLayout
      title="Overview"
      subtitle="Track spending, see what changed this month, and understand exactly where SaveBud thinks you should pay attention."
    >
      {error ? <div className="mb-6 rounded-3xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-200">{error}</div> : null}

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        <StatCard title="Total Income" value={formatCurrency(summary?.total_income)} helper="Money coming in" tone="brand" />
        <StatCard title="Total Expenses" value={formatCurrency(summary?.total_expenses)} helper="Money going out" tone="slate" />
        <StatCard title="Savings Rate" value={formatPercent(summary?.savings_rate)} helper="How much income you keep" tone="success" />
        <StatCard title="Predicted Next Month" value={formatCurrency(prediction?.predicted_amount)} helper="Expected spending ahead" tone="danger" />
        <StatCard title="Health Score" value={`${summary?.financial_health_score?.toFixed(0) || "0"}/100`} helper="Overall financial health" tone="brand" />
      </div>

      <div className="mt-8 grid gap-6 xl:grid-cols-[1.2fr,0.8fr]">
        <section className="rounded-3xl border border-white/10 bg-slate-900/60 p-6 shadow-soft">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-lg font-semibold text-white">Where You Need To Look After</h2>
              <p className="mt-1 text-sm text-slate-400">Your most important focus areas right now.</p>
            </div>
            <Link to="/recommendations" className="rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-slate-200 hover:bg-white/10">
              Open advice
            </Link>
          </div>

          <div className="mt-4 space-y-3">
            {(analysis?.attention_areas || []).map((item) => (
              <div key={item} className="rounded-2xl bg-amber-500/10 p-4 text-sm text-amber-100">
                {item}
              </div>
            ))}
            {!analysis?.attention_areas?.length ? <p className="text-sm text-slate-400">Add more transactions to unlock personalized coaching.</p> : null}
          </div>

          <div className="mt-6">
            <h3 className="text-base font-semibold text-white">Top Overspending Categories</h3>
            <div className="mt-3 space-y-3">
              {(analysis?.overspending_categories || []).map((item) => (
                <div key={item.category} className="rounded-2xl border border-red-500/20 bg-red-500/10 p-4">
                  <div className="flex items-center justify-between">
                    <p className="font-medium text-white">{item.category}</p>
                    <p className="text-sm font-semibold text-red-200">+{formatCurrency(item.difference)}</p>
                  </div>
                  <p className="mt-2 text-sm text-slate-300">
                    Current: {formatCurrency(item.current)} | Target: {formatCurrency(item.target)}
                  </p>
                </div>
              ))}
              {!analysis?.overspending_categories?.length ? <p className="text-sm text-slate-400">You are currently close to your monthly targets.</p> : null}
            </div>
          </div>
        </section>

        <section className="rounded-3xl border border-white/10 bg-slate-900/60 p-6 shadow-soft">
          <h2 className="text-lg font-semibold text-white">Quick Actions</h2>
          <div className="mt-4 space-y-3">
            {quickActions.map((item) => (
              <Link key={item.to} to={item.to} className="block rounded-2xl border border-white/10 bg-white/5 p-4 transition hover:bg-white/10">
                <p className="font-medium text-white">{item.title}</p>
                <p className="mt-1 text-sm text-slate-400">{item.description}</p>
              </Link>
            ))}
          </div>
          <div className="mt-6 rounded-2xl border border-brand-400/20 bg-brand-500/10 p-4">
            <p className="text-sm font-medium text-brand-100">Predicted next month spend</p>
            <p className="mt-2 text-3xl font-semibold text-white">{formatCurrency(prediction?.predicted_amount)}</p>
            <p className="mt-2 text-sm text-slate-300">Use this as your guide when setting next month’s spending cap.</p>
          </div>
        </section>
      </div>

      <div className="mt-8 grid gap-6 xl:grid-cols-[2fr,1fr]">
        <section className="rounded-3xl border border-white/10 bg-slate-900/60 p-6 shadow-soft">
          <h2 className="text-lg font-semibold text-white">Income vs Expense Trend</h2>
          <div className="mt-6 h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={summary?.monthly_trends || []}>
                <XAxis dataKey="month" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="income" stroke="#14b8a6" strokeWidth={3} />
                <Line type="monotone" dataKey="expense" stroke="#f87171" strokeWidth={3} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="rounded-3xl border border-white/10 bg-slate-900/60 p-6 shadow-soft">
          <h2 className="text-lg font-semibold text-white">Expense Breakdown</h2>
          <div className="mt-6 h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={summary?.category_breakdown?.filter((item) => item.transaction_type === "expense") || []} dataKey="amount" nameKey="category" outerRadius={110}>
                  {(summary?.category_breakdown?.filter((item) => item.transaction_type === "expense") || []).map((entry, index) => (
                    <Cell key={`${entry.category}-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </section>
      </div>

      <div className="mt-8 grid gap-6 xl:grid-cols-2">
        <section className="rounded-3xl border border-white/10 bg-slate-900/60 p-6 shadow-soft">
          <h2 className="text-lg font-semibold text-white">Plain-English Spend Insights</h2>
          <div className="mt-4 space-y-3">
            {(summary?.plain_english_insights || []).map((item) => (
              <div key={item} className="rounded-2xl bg-white/5 p-4 text-sm text-slate-200">
                {item}
              </div>
            ))}
          </div>
          <h3 className="mt-6 text-base font-semibold text-white">What Changed This Month</h3>
          <div className="mt-3 space-y-3">
            {(summary?.what_changed || []).map((item) => (
              <div key={item} className="rounded-2xl bg-brand-500/10 p-4 text-sm text-brand-100">
                {item}
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-3xl border border-white/10 bg-slate-900/60 p-6 shadow-soft">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-lg font-semibold text-white">Budget Progress By Category</h2>
              <p className="mt-1 text-sm text-slate-400">See your monthly cap progress at a glance.</p>
            </div>
            <Link to="/planning" className="rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-slate-200 hover:bg-white/10">
              Edit budgets
            </Link>
          </div>
          <div className="mt-4 space-y-4">
            {(summary?.budget_progress || []).map((item) => (
              <div key={item.category}>
                <div className="mb-2 flex items-center justify-between text-sm">
                  <span className="font-medium text-slate-100">{item.category}</span>
                  <span className={item.status === "over" ? "font-semibold text-red-200" : "text-slate-400"}>
                    {formatCurrency(item.current)} / {item.target ? formatCurrency(item.target) : "No cap"}
                  </span>
                </div>
                <div className="h-3 overflow-hidden rounded-full bg-white/10">
                  <div className={`h-full rounded-full ${item.status === "over" ? "bg-red-500" : "bg-brand-500"}`} style={{ width: `${Math.min((item.progress || 0) * 100, 100)}%` }} />
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <AlertPanel title="Overspending Signals" items={analysis?.overspending_signals || []} />
        <AlertPanel
          title="Risk Flags"
          items={[
            `Risk Level: ${analysis?.risk_level || "low"}`,
            `Risk Score: ${analysis?.risk_score || 0}`,
            ...(analysis?.category_flags || []),
          ]}
        />
      </div>
    </AppLayout>
  );
}
