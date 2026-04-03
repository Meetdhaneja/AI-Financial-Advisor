import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import api from "../api/client";
import AppLayout from "../layouts/AppLayout";
import { formatCurrency } from "../utils/formatters";

export default function AnalyticsPage() {
  const [summary, setSummary] = useState(null);
  const [prediction, setPrediction] = useState(null);

  useEffect(() => {
    Promise.all([api.get("/finance/summary"), api.post("/ai/predict-expense", {})]).then(([summaryRes, predictionRes]) => {
      setSummary(summaryRes.data);
      setPrediction(predictionRes.data);
    });
  }, []);

  return (
    <AppLayout title="Analytics" subtitle="Deep dive into category behavior and projected trends without the clutter.">
      <div className="grid gap-6 lg:grid-cols-[2fr,1fr]">
        <section className="rounded-3xl border border-white/10 bg-slate-900/60 p-6 shadow-soft">
          <h2 className="text-lg font-semibold text-white">Category-wise Spending</h2>
          <div className="mt-6 h-96">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={summary?.category_breakdown?.filter((item) => item.transaction_type === "expense") || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="category" angle={-20} textAnchor="end" height={70} stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip />
                <Legend />
                <Bar dataKey="amount" fill="#0f766e" radius={[12, 12, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>
        <section className="rounded-3xl border border-white/10 bg-slate-900/60 p-6 shadow-soft">
          <h2 className="text-lg font-semibold text-white">Prediction Snapshot</h2>
          <div className="mt-6 space-y-4 text-sm text-slate-300">
            <div className="rounded-2xl bg-white/5 p-4">
              <p className="text-slate-400">Predicted spend</p>
              <p className="mt-2 text-2xl font-semibold text-white">{formatCurrency(prediction?.predicted_amount)}</p>
            </div>
            <div className="rounded-2xl bg-white/5 p-4">
              <p className="text-slate-400">Confidence band</p>
              <p className="mt-2 font-semibold text-white">
                {formatCurrency(prediction?.confidence_band?.[0])} - {formatCurrency(prediction?.confidence_band?.[1])}
              </p>
            </div>
            <div className="rounded-2xl bg-white/5 p-4">
              <p className="text-slate-400">Top factors</p>
              <ul className="mt-2 space-y-2">
                {(prediction?.top_factors || []).map((factor) => (
                  <li key={factor}>{factor}</li>
                ))}
              </ul>
            </div>
          </div>
        </section>
      </div>
    </AppLayout>
  );
}
