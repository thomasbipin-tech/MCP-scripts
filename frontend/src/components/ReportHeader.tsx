import type { Deal } from '../types/report'
import { formatMoney } from '../lib/format'
import { verticalLabel } from '../lib/vertical'
import StageBadge from './StageBadge'

export default function ReportHeader({ deal, watermark }: { deal: Deal; watermark: string | null }) {
  return (
    <div className="relative overflow-hidden border-b border-slate-800 bg-slate-900/40">
      {watermark && (
        <div className="pointer-events-none absolute inset-0 flex items-center justify-center overflow-hidden">
          <span className="rotate-[-18deg] select-none whitespace-nowrap text-6xl font-extrabold uppercase tracking-widest text-signal-500/10 sm:text-7xl">
            {watermark}
          </span>
        </div>
      )}
      <div className="relative mx-auto max-w-6xl px-6 py-8">
        {watermark && (
          <div className="mb-4 inline-flex items-center gap-2 rounded border border-signal-500/40 bg-signal-500/10 px-3 py-1.5 text-xs font-semibold uppercase tracking-wide text-signal-400">
            {watermark}
          </div>
        )}
        <div className="flex flex-wrap items-start justify-between gap-6">
          <div>
            <h1 className="text-2xl font-bold text-slate-50">{deal.codename}</h1>
            <p className="mt-1 text-sm text-slate-400">{deal.entity_name}</p>
            <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-slate-500">
              <span className="rounded border border-slate-700 px-2 py-0.5">
                {deal.vertical_label ?? verticalLabel(deal.vertical)}
              </span>
              <span className="rounded border border-slate-700 px-2 py-0.5">{deal.state}</span>
              <span className="rounded border border-slate-700 px-2 py-0.5 capitalize">
                {deal.deal_type} deal
              </span>
              <span className="rounded border border-slate-700 px-2 py-0.5">{deal.tier}</span>
              <StageBadge stage={deal.stage} />
            </div>
          </div>
          <div className="text-right">
            <div className="font-mono-num text-3xl font-bold text-slate-50">
              {formatMoney(deal.asking_price)}
            </div>
            <p className="text-xs uppercase tracking-wide text-slate-500">Asking price</p>
            <div className="mt-2 font-mono-num text-lg text-slate-300">
              {formatMoney(deal.claimed_sde)}
            </div>
            <p className="text-xs uppercase tracking-wide text-slate-500">Claimed SDE</p>
          </div>
        </div>
      </div>
    </div>
  )
}
