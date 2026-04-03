import { Link, NavLink } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

const navigation = [
  { to: "/", label: "Overview", hint: "Quick summary" },
  { to: "/add-transaction", label: "Add Money", hint: "Income and expenses" },
  { to: "/analytics", label: "Analytics", hint: "Trends and patterns" },
  { to: "/planning", label: "Planning", hint: "Goals and bills" },
  { to: "/recommendations", label: "Advice", hint: "Where to improve" },
];

const linkStyle = ({ isActive }) =>
  `block rounded-2xl border px-4 py-3 transition ${
    isActive
      ? "border-brand-400 bg-brand-500/15 text-white shadow-soft"
      : "border-transparent bg-white/5 text-slate-300 hover:border-white/10 hover:bg-white/10 hover:text-white"
  }`;

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <aside className="flex h-full flex-col bg-[#0b1220] px-4 py-6 text-white">
      <Link to="/" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-4">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-brand-200">SaveBud</p>
        <p className="mt-2 text-xl font-semibold">Personal finance made simple</p>
        <p className="mt-2 text-sm text-slate-300">All your important actions are one click away.</p>
      </Link>

      <nav className="mt-6 space-y-2">
        {navigation.map((item) => (
          <NavLink key={item.to} to={item.to} className={linkStyle}>
            <p className="text-sm font-semibold">{item.label}</p>
            <p className="mt-1 text-xs text-slate-400">{item.hint}</p>
          </NavLink>
        ))}
      </nav>

      <div className="mt-auto rounded-3xl border border-white/10 bg-white/5 p-4">
        <p className="text-sm font-semibold text-white">{user?.full_name || "Your account"}</p>
        <p className="mt-1 text-xs text-slate-400">{user?.email}</p>
        <button
          onClick={logout}
          className="mt-4 w-full rounded-2xl border border-white/10 bg-white/10 px-4 py-3 text-sm font-medium text-white transition hover:bg-white/15"
        >
          Logout
        </button>
      </div>
    </aside>
  );
}
