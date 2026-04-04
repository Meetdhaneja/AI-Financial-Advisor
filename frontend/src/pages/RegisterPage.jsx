import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    monthly_income_default: "",
    risk_profile: "medium",
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const updateField = (event) => setForm({ ...form, [event.target.name]: event.target.value });

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await register({
        ...form,
        monthly_income_default: form.monthly_income_default ? Number(form.monthly_income_default) : null,
      });
      navigate("/");
    } catch (registrationError) {
      if (registrationError.code === "ERR_NETWORK") {
        setError("Could not connect to the server. Please check if the backend is running.");
      } else {
        const detail = registrationError.response?.data?.detail;
        if (Array.isArray(detail)) {
          setError(detail.map((item) => item.msg).join(", "));
        } else {
          setError(detail || "Registration failed.");
        }
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[radial-gradient(circle_at_top_left,_rgba(15,118,110,0.28),_#07111d_42%,_#020617)] px-4">
      <form onSubmit={handleSubmit} className="w-full max-w-xl rounded-[28px] border border-white/10 bg-slate-950/85 p-8 shadow-soft backdrop-blur">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-brand-100">SaveBud</p>
        <h1 className="mt-3 text-2xl font-semibold text-white">Create your account</h1>
        <p className="mt-2 text-sm text-slate-400">Set up your profile once and SaveBud will keep the rest simple.</p>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <input name="full_name" placeholder="Full name" value={form.full_name} onChange={updateField} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white placeholder:text-slate-500" required />
          <input name="email" type="email" placeholder="Email" value={form.email} onChange={updateField} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white placeholder:text-slate-500" required />
          <input name="password" type="password" placeholder="Password (min 8 characters)" value={form.password} onChange={updateField} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white placeholder:text-slate-500" minLength={8} required />
          <input
            name="monthly_income_default"
            type="number"
            placeholder="Monthly income"
            value={form.monthly_income_default}
            onChange={updateField}
            className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white placeholder:text-slate-500"
          />
          <select name="risk_profile" value={form.risk_profile} onChange={updateField} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white">
            <option value="low">Low risk</option>
            <option value="medium">Medium risk</option>
            <option value="high">High risk</option>
          </select>
        </div>
        <div className="mt-4 rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-300">
          <p className="font-semibold text-white">What does risk profile mean?</p>
          <p className="mt-2"><span className="font-medium text-brand-100">Low risk</span>: safer plan, higher emergency-fund focus, lower investment risk.</p>
          <p className="mt-2"><span className="font-medium text-brand-100">Medium risk</span>: balanced savings and investment plan for most users.</p>
          <p className="mt-2"><span className="font-medium text-brand-100">High risk</span>: more aggressive investment mix with higher ups and downs.</p>
        </div>
        {error ? <p className="mt-3 text-sm text-red-300">{error}</p> : null}
        <button disabled={submitting} className="mt-6 rounded-2xl bg-brand-500 px-5 py-3 font-semibold text-white hover:bg-brand-600 disabled:opacity-70">
          {submitting ? "Creating account..." : "Create account"}
        </button>
        <p className="mt-4 text-sm text-slate-400">
          Already registered?{" "}
          <Link to="/login" className="font-medium text-brand-200">
            Login
          </Link>
        </p>
      </form>
    </div>
  );
}
