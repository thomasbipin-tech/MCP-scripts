import type { DataGap } from '../types/report'

export default function DataGaps({ gaps, intro }: { gaps: DataGap[]; intro?: string }) {
  return (
    <div className="rounded border border-slate-800 bg-slate-900/40 p-6">
      <h2 className="mb-1 text-sm font-semibold uppercase tracking-wide text-slate-300">Data gaps</h2>
      {intro && <p className="mb-4 text-xs text-slate-500">{intro}</p>}
      {gaps.length === 0 ? (
        <p className="text-sm text-slate-500">No outstanding data gaps.</p>
      ) : (
        <ul className="space-y-2">
          {gaps.map((gap) => (
            <li key={gap.key} className="flex items-center gap-3 text-sm text-slate-300">
              <span className="flex h-4 w-4 shrink-0 items-center justify-center rounded-sm border border-slate-600" />
              {gap.label}
              <span className="ml-auto text-[11px] uppercase tracking-wide text-slate-600">
                not provided
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
