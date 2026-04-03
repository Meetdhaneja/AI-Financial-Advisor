import { useState } from "react";
import api from "../api/client";

const initialForm = {
  name: "",
  goal_type: "emergency_fund",
  target_amount: "",
  current_amount: "",
  target_months: "",
  notes: "",
};

export default function GoalPlanner({ goals, onRefresh }) {
  const [form, setForm] = useState(initialForm);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const submit = async (event) => {
    event.preventDefault();
    setSaving(true);
    setError("");
    setMessage("");
    try {
      await api.post("/ai/goals", {
        ...form,
        target_amount: Number(form.target_amount),
        current_amount: Number(form.current_amount || 0),
        target_months: form.target_months ? Number(form.target_months) : null,
      });
      setForm(initialForm);
      setMessage("Savings goal added.");
      onRefresh?.();
    } catch (submissionError) {
      setError(submissionError.response?.data?.detail || "Could not save the goal.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <section className="rounded-3xl border border-white/10 bg-slate-900/60 p-6 shadow-soft">
      <h2 className="text-lg font-semibold text-white">Goal-Based Savings</h2>
      <div className="mt-4 space-y-3">
        {(goals || []).map((goal) => {
          const progress = goal.target_amount ? Math.min((goal.current_amount / goal.target_amount) * 100, 100) : 0;
          return (
            <div key={goal.id} className="rounded-2xl bg-white/5 p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-white">{goal.name}</p>
                  <p className="text-sm text-slate-400">{goal.goal_type.replaceAll("_", " ")}</p>
                </div>
                <p className="text-sm font-semibold text-slate-200">{progress.toFixed(0)}%</p>
              </div>
              <div className="mt-3 h-3 overflow-hidden rounded-full bg-white/10">
                <div className="h-full rounded-full bg-brand-500" style={{ width: `${progress}%` }} />
              </div>
              <p className="mt-2 text-sm text-slate-300">
                Saved Rs {goal.current_amount} of Rs {goal.target_amount}
              </p>
            </div>
          );
        })}
      </div>

      <form onSubmit={submit} className="mt-6 grid gap-4 md:grid-cols-2">
        <input className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white placeholder:text-slate-500" placeholder="Goal name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
        <select className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white" value={form.goal_type} onChange={(e) => setForm({ ...form, goal_type: e.target.value })}>
          <option value="emergency_fund">Emergency fund</option>
          <option value="vacation">Vacation</option>
          <option value="car">Car</option>
          <option value="education">Education</option>
          <option value="house_down_payment">House down payment</option>
        </select>
        <input className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white placeholder:text-slate-500" placeholder="Target amount" type="number" min="1" value={form.target_amount} onChange={(e) => setForm({ ...form, target_amount: e.target.value })} required />
        <input className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white placeholder:text-slate-500" placeholder="Current amount" type="number" value={form.current_amount} onChange={(e) => setForm({ ...form, current_amount: e.target.value })} />
        <input className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white placeholder:text-slate-500" placeholder="Target months" type="number" value={form.target_months} onChange={(e) => setForm({ ...form, target_months: e.target.value })} />
        <input className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white placeholder:text-slate-500" placeholder="Notes" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
        <button className="rounded-2xl bg-brand-500 px-5 py-3 text-sm font-semibold text-white hover:bg-brand-600 md:col-span-2" disabled={saving}>
          {saving ? "Saving..." : "Add Savings Goal"}
        </button>
        {message ? <p className="text-sm text-green-300 md:col-span-2">{message}</p> : null}
        {error ? <p className="text-sm text-red-300 md:col-span-2">{error}</p> : null}
      </form>
    </section>
  );
}
