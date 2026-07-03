import type { SeverityCounts } from '../types/report'
import { SEVERITY_CLASSES, SEVERITY_LABEL, SEVERITY_ORDER } from '../lib/severity'

export default function SeverityTiles({ counts }: { counts: SeverityCounts }) {
  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
      {SEVERITY_ORDER.map((sev) => {
        const cls = SEVERITY_CLASSES[sev]
        const empty = counts[sev] === 0
        // These are read-only counts, not buttons. Uniform border on every tile,
        // severity shown only via the number's color and a small left accent
        // bar; a zero-count tile is dimmed so it never reads as "selected".
        return (
          <div
            key={sev}
            className={`relative select-none overflow-hidden rounded border border-slate-800 bg-slate-900/40 px-5 py-4 ${
              empty ? 'opacity-50' : ''
            }`}
          >
            <span className={`absolute inset-y-0 left-0 w-1 ${cls.dot} ${empty ? 'opacity-40' : ''}`} />
            <div className={`font-mono-num text-4xl font-bold ${empty ? 'text-slate-500' : cls.text}`}>
              {counts[sev]}
            </div>
            <div className="mt-1 text-xs uppercase tracking-wide text-slate-500">
              {SEVERITY_LABEL[sev]}
            </div>
          </div>
        )
      })}
    </div>
  )
}
