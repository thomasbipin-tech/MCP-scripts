export default function ExecutiveSummary({ items }: { items: string[] }) {
  if (items.length === 0) return null
  const [headline, ...rest] = items
  return (
    <div className="rounded border border-slate-800 bg-slate-900/40 p-6">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-300">
        Executive summary
      </h2>
      <p className="mb-4 text-sm leading-relaxed text-slate-300">{headline}</p>
      {rest.length > 0 && (
        <ul className="space-y-2">
          {rest.map((item, i) => (
            <li key={i} className="flex gap-2 text-sm text-slate-400">
              <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-signal-500" />
              {item}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
