export default function StatCard({ title, value, helper, tone = "slate" }) {
  const toneStyles = {
    slate: "border-white/10 bg-slate-900/60",
    brand: "border-brand-400/20 bg-brand-500/10",
    success: "border-green-500/20 bg-green-500/10",
    danger: "border-red-500/20 bg-red-500/10",
  };

  return (
    <div className={`rounded-2xl border p-5 shadow-soft ${toneStyles[tone] || toneStyles.slate}`}>
      <p className="text-sm font-medium text-slate-400">{title}</p>
      <h3 className="mt-3 text-3xl font-semibold text-white">{value}</h3>
      {helper ? <p className="mt-2 text-sm text-slate-400">{helper}</p> : null}
    </div>
  );
}
