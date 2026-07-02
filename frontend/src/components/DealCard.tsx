import { Link } from 'react-router-dom'
import StageBadge from './StageBadge'
import { formatMoney } from '../lib/format'
import type { SeverityCounts } from '../types/report'
import { SEVERITY_CLASSES } from '../lib/severity'

export interface DealCardData {
  codename: string
  vertical_label: string
  asking_price: string
  stage: string
  severity_counts: SeverityCounts
  linkTo?: string
}

export default function DealCard({ deal }: { deal: DealCardData }) {
  const content = (
    <div className="flex h-full flex-col rounded border border-slate-800 bg-slate-900/40 p-5 transition hover:border-slate-600">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="truncate text-sm font-semibold text-slate-100">{deal.codename}</h3>
          <p className="mt-0.5 truncate text-xs text-slate-500">{deal.vertical_label}</p>
        </div>
        <StageBadge stage={deal.stage} />
      </div>

      <div className="mt-4 font-mono-num text-xl font-semibold text-slate-50">
        {formatMoney(deal.asking_price)}
      </div>
      <p className="text-[11px] uppercase tracking-wide text-slate-600">Asking price</p>

      <div className="mt-4 grid grid-cols-4 gap-2 border-t border-slate-800 pt-4">
        {(['CRITICAL', 'HIGH', 'MEDIUM', 'INFO'] as const).map((sev) => (
          <div key={sev} className="text-center">
            <div className={`font-mono-num text-base font-semibold ${SEVERITY_CLASSES[sev].text}`}>
              {deal.severity_counts[sev]}
            </div>
            <div className="text-[9px] uppercase tracking-wide text-slate-600">{sev}</div>
          </div>
        ))}
      </div>
    </div>
  )

  if (deal.linkTo) {
    return (
      <Link to={deal.linkTo} className="block h-full">
        {content}
      </Link>
    )
  }
  return content
}
