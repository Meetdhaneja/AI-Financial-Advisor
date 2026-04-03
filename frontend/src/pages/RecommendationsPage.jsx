import { useEffect, useState } from "react";
import api from "../api/client";
import AppLayout from "../layouts/AppLayout";

export default function RecommendationsPage() {
  const [recommendation, setRecommendation] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    Promise.all([api.get("/ai/recommend-budget"), api.get("/ai/recommendations")]).then(([budgetRes, historyRes]) => {
      setRecommendation(budgetRes.data);
      setHistory(historyRes.data);
    });
  }, []);

  return (
    <AppLayout title="Recommendations" subtitle="Budget, emergency fund, and investment guidance personalized to your profile.">
      <div className="grid gap-6 lg:grid-cols-[1.4fr,1fr]">
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-soft">
          <h2 className="text-lg font-semibold text-slate-900">Recommended Budget Plan</h2>
          <div className="mt-6 grid gap-4 md:grid-cols-2">
            {Object.entries(recommendation?.budget_plan || {}).map(([key, value]) => (
              <div key={key} className="rounded-xl bg-slate-50 p-4">
                <p className="text-sm capitalize text-slate-500">{key}</p>
                <p className="mt-2 text-2xl font-semibold text-slate-900">₹{Number(value).toFixed(0)}</p>
              </div>
            ))}
          </div>
          <div className="mt-6 rounded-xl border border-brand-100 bg-brand-50 p-5">
            <p className="text-sm text-brand-900">Emergency fund target</p>
            <p className="mt-2 text-3xl font-semibold text-brand-900">₹{recommendation?.emergency_fund_target?.toFixed(0) || "0"}</p>
          </div>
          <div className="mt-6">
            <h3 className="text-base font-semibold text-slate-900">Investment Allocation</h3>
            <div className="mt-3 space-y-3">
              {Object.entries(recommendation?.investment_allocation || {}).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between rounded-xl bg-slate-50 px-4 py-3">
                  <span className="capitalize text-slate-600">{key.replace("_", " ")}</span>
                  <span className="font-semibold text-slate-900">{value}%</span>
                </div>
              ))}
            </div>
          </div>
          <div className="mt-6">
            <h3 className="text-base font-semibold text-slate-900">Next Actions</h3>
            <ul className="mt-3 space-y-2 text-sm text-slate-600">
              {(recommendation?.next_actions || []).map((action) => (
                <li key={action} className="rounded-xl bg-slate-50 p-4">
                  {action}
                </li>
              ))}
            </ul>
          </div>
        </section>
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-soft">
          <h2 className="text-lg font-semibold text-slate-900">Recommendation History</h2>
          <div className="mt-4 space-y-3">
            {history.length ? (
              history.map((item) => (
                <article key={item.id} className="rounded-xl bg-slate-50 p-4">
                  <p className="text-sm font-semibold text-slate-900">{item.title}</p>
                  <p className="mt-2 text-sm text-slate-600">{item.message}</p>
                  <p className="mt-2 text-xs text-slate-400">{new Date(item.created_at).toLocaleString()}</p>
                </article>
              ))
            ) : (
              <p className="text-sm text-slate-500">No recommendations generated yet.</p>
            )}
          </div>
        </section>
      </div>
    </AppLayout>
  );
}

