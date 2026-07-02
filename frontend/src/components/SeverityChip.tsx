import type { Severity } from '../types/report'
import { SEVERITY_CLASSES, SEVERITY_LABEL } from '../lib/severity'

export default function SeverityChip({ severity }: { severity: Severity }) {
  const cls = SEVERITY_CLASSES[severity]
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded border px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide ${cls.chip}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${cls.dot}`} />
      {SEVERITY_LABEL[severity]}
    </span>
  )
}
