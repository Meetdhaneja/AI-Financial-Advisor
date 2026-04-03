export default function AlertPanel({ title, items }) {
  return (
    <section className="rounded-3xl border border-white/10 bg-slate-900/60 p-6 shadow-soft">
      <h2 className="text-lg font-semibold text-white">{title}</h2>
      <div className="mt-4 space-y-3">
        {items?.length ? (
          items.map((item) => (
            <div key={item} className="rounded-2xl bg-white/5 p-4 text-sm text-slate-200">
              {item}
            </div>
          ))
        ) : (
          <p className="text-sm text-slate-400">No alerts right now.</p>
        )}
      </div>
    </section>
  );
}
