import { useEffect, useState } from "react";
import api from "../api/client";

const initialState = {
  category_id: "",
  amount: "",
  transaction_type: "expense",
  occurred_at: new Date().toISOString().slice(0, 10),
  description: "",
};

export default function TransactionForm({ onSuccess }) {
  const [categories, setCategories] = useState([]);
  const [form, setForm] = useState(initialState);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [loadingCategories, setLoadingCategories] = useState(true);

  useEffect(() => {
    const loadCategories = async () => {
      setLoadingCategories(true);
      try {
        const { data } = await api.get("/transactions/categories");
        setCategories(data);
      } catch {
        setError("Unable to load categories right now.");
      } finally {
        setLoadingCategories(false);
      }
    };
    loadCategories();
  }, []);

  const filteredCategories = categories.filter((category) => category.type === form.transaction_type);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({
      ...current,
      [name]: value,
      category_id: name === "transaction_type" ? "" : current.category_id,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await api.post("/transactions", {
        ...form,
        category_id: Number(form.category_id),
        amount: Number(form.amount),
      });
      setForm(initialState);
      onSuccess?.();
    } catch (submissionError) {
      setError(submissionError.response?.data?.detail || "Unable to add transaction.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-soft">
      <div className="grid gap-4 md:grid-cols-2">
        <label className="space-y-2 text-sm">
          <span className="font-medium text-slate-700">Type</span>
          <select
            name="transaction_type"
            value={form.transaction_type}
            onChange={handleChange}
            className="w-full rounded-xl border border-slate-200 px-4 py-3"
          >
            <option value="expense">Expense</option>
            <option value="income">Income</option>
          </select>
        </label>
        <label className="space-y-2 text-sm">
          <span className="font-medium text-slate-700">Category</span>
          <select
            name="category_id"
            value={form.category_id}
            onChange={handleChange}
            className="w-full rounded-xl border border-slate-200 px-4 py-3"
            required
            disabled={loadingCategories}
          >
            <option value="">{loadingCategories ? "Loading categories..." : "Select category"}</option>
            {filteredCategories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </label>
        <label className="space-y-2 text-sm">
          <span className="font-medium text-slate-700">Amount</span>
          <input
            name="amount"
            type="number"
            step="0.01"
            min="0.01"
            value={form.amount}
            onChange={handleChange}
            className="w-full rounded-xl border border-slate-200 px-4 py-3"
            required
          />
        </label>
        <label className="space-y-2 text-sm">
          <span className="font-medium text-slate-700">Date</span>
          <input
            name="occurred_at"
            type="date"
            value={form.occurred_at}
            onChange={handleChange}
            className="w-full rounded-xl border border-slate-200 px-4 py-3"
            required
          />
        </label>
      </div>
      <label className="mt-4 block space-y-2 text-sm">
        <span className="font-medium text-slate-700">Notes</span>
        <textarea
          name="description"
          value={form.description}
          onChange={handleChange}
          className="min-h-28 w-full rounded-xl border border-slate-200 px-4 py-3"
          placeholder="Optional transaction notes"
        />
      </label>
      {error ? <p className="mt-3 text-sm text-red-600">{error}</p> : null}
      <button
        type="submit"
        disabled={submitting}
        className="mt-5 rounded-full bg-brand-500 px-5 py-3 text-sm font-semibold text-white hover:bg-brand-600 disabled:opacity-70"
      >
        {submitting ? "Saving..." : "Save Transaction"}
      </button>
    </form>
  );
}
