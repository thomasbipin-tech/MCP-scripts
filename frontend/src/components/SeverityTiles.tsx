import type { SeverityCounts } from '../types/report'
import { SEVERITY_CLASSES, SEVERITY_LABEL, SEVERITY_ORDER } from '../lib/severity'

export default function SeverityTiles({ counts }: { counts: SeverityCounts }) {
  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
      {SEVERITY_ORDER.map((sev) => {
        const cls = SEVERITY_CLASSES[sev]
        return (
          <div
            key={sev}
            className={`rounded border-l-2 border border-slate-800 bg-slate-900/40 px-5 py-4 ${cls.border}`}
          >
            <div className={`font-mono-num text-4xl font-bold ${cls.text}`}>{counts[sev]}</div>
            <div className="mt-1 text-xs uppercase tracking-wide text-slate-500">
              {SEVERITY_LABEL[sev]}
            </div>
          </div>
        )
      })}
    </div>
  )
}
