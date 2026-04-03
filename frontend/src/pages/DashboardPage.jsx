import { useEffect, useState } from "react";
import { Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Cell, Legend } from "recharts";
import api from "../api/client";
import AlertPanel from "../components/AlertPanel";
import StatCard from "../components/StatCard";
import AppLayout from "../layouts/AppLayout";

const COLORS = ["#0f766e", "#0ea5e9", "#f59e0b", "#ef4444", "#8b5cf6", "#14b8a6"];

export default function DashboardPage() {
  const [summary, setSummary] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [analysis, setAnalysis] = useState(null);

  useEffect(() => {
    Promise.all([
      api.get("/finance/summary"),
      api.post("/ai/predict-expense", {}),
      api.post("/ai/analyze-spending", {}),
    ]).then(([summaryRes, predictionRes, analysisRes]) => {
      setSummary(summaryRes.data);
      setPrediction(predictionRes.data);
      setAnalysis(analysisRes.data);
    });
  }, []);

  return (
    <AppLayout title="Finance Dashboard" subtitle="A real-time view of cash flow, risk, and projected spending.">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard title="Total Income" value={`₹${summary?.total_income?.toFixed(0) || "0"}`} helper="Aggregated across your records" tone="brand" />
        <StatCard title="Total Expenses" value={`₹${summary?.total_expenses?.toFixed(0) || "0"}`} helper="Tracked expense outflow" tone="slate" />
        <StatCard title="Savings Rate" value={`${((summary?.savings_rate || 0) * 100).toFixed(1)}%`} helper="Net cashflow as a share of income" tone="success" />
        <StatCard title="Predicted Next Month" value={`₹${prediction?.predicted_amount?.toFixed(0) || "0"}`} helper="Estimated future spending" tone="danger" />
      </div>

      <div className="mt-8 grid gap-6 xl:grid-cols-[2fr,1fr]">
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-soft">
          <h2 className="text-lg font-semibold text-slate-900">Income vs Expense Trend</h2>
          <div className="mt-6 h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={summary?.monthly_trends || []}>
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="income" stroke="#0f766e" strokeWidth={3} />
                <Line type="monotone" dataKey="expense" stroke="#ef4444" strokeWidth={3} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </section>
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-soft">
          <h2 className="text-lg font-semibold text-slate-900">Expense Breakdown</h2>
          <div className="mt-6 h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={summary?.category_breakdown?.filter((item) => item.transaction_type === "expense") || []} dataKey="amount" nameKey="category" outerRadius={110}>
                  {(summary?.category_breakdown || []).map((entry, index) => (
                    <Cell key={`${entry.category}-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
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

