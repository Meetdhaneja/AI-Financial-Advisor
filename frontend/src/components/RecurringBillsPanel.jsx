import { useEffect, useState } from "react";
import api from "../api/client";

const initialForm = {
  category_id: "",
  name: "",
  amount: "",
  transaction_type: "expense",
  frequency: "monthly",
  day_of_month: 1,
};

export default function RecurringBillsPanel({ onRefresh }) {
  const [categories, setCategories] = useState([]);
  const [items, setItems] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const [categoriesRes, recurringRes] = await Promise.all([api.get("/transactions/categories"), api.get("/ai/recurring")]);
      setCategories(categoriesRes.data);
      setItems(recurringRes.data);
      setError("");
    } catch {
      setError("Unable to load recurring bills right now.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const filteredCategories = categories.filter((item) => item.type === form.transaction_type);

  const submit = async (event) => {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      await api.post("/ai/recurring", {
        ...form,
        category_id: Number(form.category_id),
        amount: Number(form.amount),
        day_of_month: Number(form.day_of_month),
      });
      setForm(initialForm);
      await load();
      onRefresh?.();
    } catch (submissionError) {
      setError(submissionError.response?.data?.detail || "Could not add recurring item.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <section className="rounded-3xl border border-white/10 bg-slate-900/60 p-6 shadow-soft">
      <h2 className="text-lg font-semibold text-white">Recurring Transactions and Bills</h2>
      <div className="mt-4 space-y-3">
        {loading ? <p className="text-sm text-slate-400">Loading recurring items...</p> : null}
        {items.map((item) => (
          <div key={item.id} className="rounded-2xl bg-white/5 p-4 text-sm text-slate-200">
            <div className="flex items-center justify-between">
              <span className="font-medium">{item.name}</span>
              <span>Rs {item.amount}</span>
            </div>
            <p className="mt-1 text-slate-400">
              {item.frequency} on day {item.day_of_month}
            </p>
          </div>
        ))}
      </div>
      <form onSubmit={submit} className="mt-6 grid gap-4 md:grid-cols-2">
        <input className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white placeholder:text-slate-500" placeholder="Bill name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
        <select className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white" value={form.transaction_type} onChange={(e) => setForm({ ...form, transaction_type: e.target.value })}>
          <option value="expense">Expense</option>
          <option value="income">Income</option>
        </select>
        <select className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white" value={form.category_id} onChange={(e) => setForm({ ...form, category_id: e.target.value })} required>
          <option value="">Choose category</option>
          {filteredCategories.map((category) => (
            <option key={category.id} value={category.id}>
              {category.name}
            </option>
          ))}
        </select>
        <input className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white placeholder:text-slate-500" type="number" min="0.01" step="0.01" placeholder="Amount" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} required />
        <input className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white placeholder:text-slate-500" type="number" min="1" max="28" placeholder="Day of month" value={form.day_of_month} onChange={(e) => setForm({ ...form, day_of_month: e.target.value })} required />
        <button className="rounded-2xl bg-brand-500 px-5 py-3 text-sm font-semibold text-white hover:bg-brand-600 md:col-span-2 disabled:opacity-70" disabled={saving}>{saving ? "Saving..." : "Add Recurring Item"}</button>
        {error ? <p className="text-sm text-red-300 md:col-span-2">{error}</p> : null}
      </form>
    </section>
  );
}
