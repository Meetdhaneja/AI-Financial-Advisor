import { useEffect, useState } from "react";
import api from "../api/client";
import AppLayout from "../layouts/AppLayout";
import { formatCurrency } from "../utils/formatters";

export default function RecommendationsExperiencePage() {
  const [recommendation, setRecommendation] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    Promise.all([api.get("/ai/recommend-budget"), api.get("/ai/recommendations")]).then(([budgetRes, historyRes]) => {
      setRecommendation(budgetRes.data);
      setHistory(historyRes.data);
    });
  }, []);

  return (
    <AppLayout title="Advice" subtitle="Understand your plan, where you overspend, and what to improve next month.">
      <div className="grid gap-6 lg:grid-cols-[1.4fr,1fr]">
        <section className="rounded-3xl border border-white/10 bg-slate-900/60 p-6 shadow-soft">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-lg font-semibold text-white">Recommended Budget Plan</h2>
              <p className="mt-1 text-sm text-slate-400">
                {recommendation?.custom_budget_used ? "Using your custom monthly preferences." : "Using AI-generated default budget guidance."}
              </p>
            </div>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2">
            {Object.entries(recommendation?.budget_plan || {}).map(([key, value]) => (
              <div key={key} className="rounded-2xl bg-white/5 p-4">
                <p className="text-sm capitalize text-slate-400">{key.replaceAll("_", " ")}</p>
                <p className="mt-2 text-2xl font-semibold text-white">{formatCurrency(value)}</p>
              </div>
            ))}
          </div>

          <div className="mt-6 rounded-2xl border border-brand-400/20 bg-brand-500/10 p-5">
            <p className="text-sm text-brand-100">Emergency fund target</p>
            <p className="mt-2 text-3xl font-semibold text-white">{formatCurrency(recommendation?.emergency_fund_target)}</p>
          </div>

          <div className="mt-6">
            <h3 className="text-base font-semibold text-white">Where You Are Overspending</h3>
            <div className="mt-3 space-y-3">
              {(recommendation?.overspending_categories || []).map((item) => (
                <div key={item.category} className="rounded-2xl border border-red-500/20 bg-red-500/10 p-4">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-white">{item.category}</span>
                    <span className="text-sm font-semibold text-red-200">+{formatCurrency(item.difference)}</span>
                  </div>
                  <p className="mt-2 text-sm text-slate-300">
                    Current {formatCurrency(item.current)} vs target {formatCurrency(item.target)}
                  </p>
                </div>
              ))}
              {!recommendation?.overspending_categories?.length ? <p className="text-sm text-slate-400">No major overspending buckets right now.</p> : null}
            </div>
          </div>

          <div className="mt-6">
            <h3 className="text-base font-semibold text-white">What Needs Attention</h3>
            <ul className="mt-3 space-y-2 text-sm text-slate-300">
              {(recommendation?.attention_areas || []).map((action) => (
                <li key={action} className="rounded-2xl bg-amber-500/10 p-4 text-amber-100">
                  {action}
                </li>
              ))}
            </ul>
          </div>

          <div className="mt-6">
            <h3 className="text-base font-semibold text-white">Next Actions</h3>
            <ul className="mt-3 space-y-2 text-sm text-slate-300">
              {(recommendation?.next_actions || []).map((action) => (
                <li key={action} className="rounded-2xl bg-white/5 p-4">
                  {action}
                </li>
              ))}
            </ul>
          </div>
        </section>

        <section className="rounded-3xl border border-white/10 bg-slate-900/60 p-6 shadow-soft">
          <h2 className="text-lg font-semibold text-white">Recommendation History</h2>
          <div className="mt-4 space-y-3">
            {history.length ? (
              history.map((item) => (
                <article key={item.id} className="rounded-2xl bg-white/5 p-4">
                  <p className="text-sm font-semibold text-white">{item.title}</p>
                  <p className="mt-2 text-sm text-slate-300">{item.message}</p>
                  <p className="mt-2 text-xs text-slate-500">{new Date(item.created_at).toLocaleString()}</p>
                </article>
              ))
            ) : (
              <p className="text-sm text-slate-400">No recommendations generated yet.</p>
            )}
          </div>
        </section>
      </div>
    </AppLayout>
  );
}
