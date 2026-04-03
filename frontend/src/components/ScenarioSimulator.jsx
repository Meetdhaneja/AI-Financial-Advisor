import { useState } from "react";
import api from "../api/client";
import { formatCurrency, formatPercent } from "../utils/formatters";

export default function ScenarioSimulator() {
  const [form, setForm] = useState({ income_change: 0, expense_change: 0, savings_change: 0 });
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [running, setRunning] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    setRunning(true);
    setError("");
    try {
      const { data } = await api.post("/ai/simulate-scenario", {
        income_change: Number(form.income_change),
        expense_change: Number(form.expense_change),
        savings_change: Number(form.savings_change),
      });
      setResult(data);
    } catch (simulationError) {
      setError(simulationError.response?.data?.detail || "Could not run the scenario.");
    } finally {
      setRunning(false);
    }
  };

  return (
    <section className="rounded-3xl border border-white/10 bg-slate-900/60 p-6 shadow-soft">
      <h2 className="text-lg font-semibold text-white">Scenario Simulator</h2>
      <form onSubmit={submit} className="mt-4 grid gap-4 md:grid-cols-3">
        <input className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white placeholder:text-slate-500" type="number" placeholder="Income change" value={form.income_change} onChange={(e) => setForm({ ...form, income_change: e.target.value })} />
        <input className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white placeholder:text-slate-500" type="number" placeholder="Expense change" value={form.expense_change} onChange={(e) => setForm({ ...form, expense_change: e.target.value })} />
        <input className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white placeholder:text-slate-500" type="number" placeholder="Savings change" value={form.savings_change} onChange={(e) => setForm({ ...form, savings_change: e.target.value })} />
        <button className="rounded-2xl bg-brand-500 px-5 py-3 text-sm font-semibold text-white hover:bg-brand-600 md:col-span-3 disabled:opacity-70" disabled={running}>{running ? "Running..." : "Run Scenario"}</button>
      </form>
      {error ? <p className="mt-4 text-sm text-red-300">{error}</p> : null}
      {result ? (
        <div className="mt-5 grid gap-3 md:grid-cols-2">
          <div className="rounded-2xl bg-white/5 p-4 text-slate-200">Projected income: {formatCurrency(result.projected_income)}</div>
          <div className="rounded-2xl bg-white/5 p-4 text-slate-200">Projected expenses: {formatCurrency(result.projected_expenses)}</div>
          <div className="rounded-2xl bg-white/5 p-4 text-slate-200">Projected savings: {formatCurrency(result.projected_savings)}</div>
          <div className="rounded-2xl bg-white/5 p-4 text-slate-200">Projected savings rate: {formatPercent(result.projected_savings_rate)}</div>
          <div className="rounded-2xl bg-amber-500/10 p-4 md:col-span-2 text-amber-100">{result.message}</div>
        </div>
      ) : null}
    </section>
  );
}
