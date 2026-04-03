import { useEffect, useMemo, useState } from "react";
import api from "../api/client";

const TRACKED_CATEGORIES = [
  "Rent",
  "Groceries",
  "Transportation",
  "Utilities",
  "Healthcare",
  "Dining & Entertainment",
  "Shopping & Wants",
  "EMI/Loans",
];

export default function BudgetPreferencesForm({ user, onSaved }) {
  const initialState = useMemo(
    () => ({
      monthly_income_default: user?.monthly_income_default || "",
      monthly_budget_target: user?.monthly_budget_target || "",
      preferred_savings_rate: user?.preferred_savings_rate || 0.2,
      risk_profile: user?.risk_profile || "medium",
      category_budget_preferences: TRACKED_CATEGORIES.reduce((acc, category) => {
        acc[category] = user?.category_budget_preferences?.[category] || "";
        return acc;
      }, {}),
    }),
    [user],
  );

  const [form, setForm] = useState(initialState);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    setForm(initialState);
  }, [initialState]);

  const updateCategory = (category, value) => {
    setForm((current) => ({
      ...current,
      category_budget_preferences: {
        ...current.category_budget_preferences,
        [category]: value,
      },
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSaving(true);
    setMessage("");
    try {
      const payload = {
        monthly_income_default: form.monthly_income_default ? Number(form.monthly_income_default) : null,
        monthly_budget_target: form.monthly_budget_target ? Number(form.monthly_budget_target) : null,
        preferred_savings_rate: Number(form.preferred_savings_rate),
        risk_profile: form.risk_profile,
        category_budget_preferences: Object.fromEntries(
          Object.entries(form.category_budget_preferences)
            .filter(([, value]) => value !== "" && value !== null)
            .map(([key, value]) => [key, Number(value)]),
        ),
      };
      const { data } = await api.put("/auth/me/preferences", payload);
      setMessage("Budget preferences updated.");
      onSaved?.(data);
    } catch {
      setMessage("Could not save preferences right now.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="rounded-3xl border border-white/10 bg-slate-900/60 p-6 shadow-soft">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-white">Customize Your Monthly Plan</h2>
          <p className="mt-1 text-sm text-slate-400">Set simple monthly targets so SaveBud can flag overspending more accurately.</p>
        </div>
        <button type="submit" disabled={saving} className="rounded-2xl bg-brand-500 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-600 disabled:opacity-70">
          {saving ? "Saving..." : "Save Plan"}
        </button>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <label className="space-y-2 text-sm">
          <span className="font-medium text-slate-300">Monthly income</span>
          <input
            type="number"
            value={form.monthly_income_default}
            onChange={(event) => setForm({ ...form, monthly_income_default: event.target.value })}
            className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white"
          />
        </label>
        <label className="space-y-2 text-sm">
          <span className="font-medium text-slate-300">Monthly spending target</span>
          <input
            type="number"
            value={form.monthly_budget_target}
            onChange={(event) => setForm({ ...form, monthly_budget_target: event.target.value })}
            className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white"
          />
        </label>
        <label className="space-y-2 text-sm">
          <span className="font-medium text-slate-300">Preferred savings rate</span>
          <input
            type="number"
            step="0.01"
            min="0"
            max="1"
            value={form.preferred_savings_rate}
            onChange={(event) => setForm({ ...form, preferred_savings_rate: event.target.value })}
            className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white"
          />
        </label>
        <label className="space-y-2 text-sm">
          <span className="font-medium text-slate-300">Risk profile</span>
          <select value={form.risk_profile} onChange={(event) => setForm({ ...form, risk_profile: event.target.value })} className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white">
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </label>
      </div>

      <div className="mt-6">
        <h3 className="text-base font-semibold text-white">Category Budget Caps</h3>
        <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {TRACKED_CATEGORIES.map((category) => (
            <label key={category} className="space-y-2 text-sm">
              <span className="font-medium text-slate-300">{category}</span>
              <input
                type="number"
                value={form.category_budget_preferences[category]}
                onChange={(event) => updateCategory(category, event.target.value)}
                className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white placeholder:text-slate-500"
                placeholder="Optional"
              />
            </label>
          ))}
        </div>
      </div>
      {message ? <p className="mt-4 text-sm text-slate-300">{message}</p> : null}
    </form>
  );
}
