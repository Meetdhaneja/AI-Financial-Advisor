import Navbar from "../components/Navbar";

export default function AppLayout({ title, subtitle, children }) {
  return (
    <div className="min-h-screen bg-[#07111d] text-slate-100 lg:grid lg:grid-cols-[280px,1fr]">
      <div className="border-b border-white/10 lg:min-h-screen lg:border-b-0 lg:border-r lg:border-white/10">
        <Navbar />
      </div>
      <main className="min-w-0">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-10 lg:py-8">
          <div className="mb-8 rounded-3xl border border-white/10 bg-[linear-gradient(135deg,rgba(15,118,110,0.18),rgba(15,23,42,0.92))] p-6 shadow-soft">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-brand-100">SaveBud</p>
            <h1 className="mt-3 text-3xl font-semibold text-white">{title}</h1>
            {subtitle ? <p className="mt-2 max-w-3xl text-slate-300">{subtitle}</p> : null}
          </div>
          {children}
        </div>
      </main>
    </div>
  );
}
