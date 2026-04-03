import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      await login(form.email, form.password);
      navigate("/");
    } catch (loginError) {
      setError(loginError.response?.data?.detail || "Login failed.");
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[radial-gradient(circle_at_top_left,_rgba(15,118,110,0.28),_#07111d_42%,_#020617)] px-4">
      <form onSubmit={handleSubmit} className="w-full max-w-md rounded-[28px] border border-white/10 bg-slate-950/85 p-8 shadow-soft backdrop-blur">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-brand-100">SaveBud</p>
        <h1 className="mt-3 text-2xl font-semibold text-white">Welcome back</h1>
        <p className="mt-2 text-sm text-slate-400">Sign in and see the simple version of your money story.</p>
        <div className="mt-6 space-y-4">
          <input
            type="email"
            placeholder="Email"
            value={form.email}
            onChange={(event) => setForm({ ...form, email: event.target.value })}
            className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white placeholder:text-slate-500"
          />
          <input
            type="password"
            placeholder="Password"
            value={form.password}
            onChange={(event) => setForm({ ...form, password: event.target.value })}
            className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white placeholder:text-slate-500"
          />
        </div>
        {error ? <p className="mt-3 text-sm text-red-300">{error}</p> : null}
        <button className="mt-6 w-full rounded-2xl bg-brand-500 px-4 py-3 font-semibold text-white hover:bg-brand-600">
          Login
        </button>
        <p className="mt-4 text-sm text-slate-400">
          No account?{" "}
          <Link to="/register" className="font-medium text-brand-200">
            Create one
          </Link>
        </p>
      </form>
    </div>
  );
}
