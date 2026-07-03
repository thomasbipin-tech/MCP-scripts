import type { Benchmarks, Deal } from '../types/report'
import { formatMultiple } from '../lib/format'

export default function BenchmarkPanel({ benchmarks, deal }: { benchmarks: Benchmarks; deal: Deal }) {
  const bm = benchmarks?.sde_multiple
  if (!bm) {
    return (
      <div className="rounded border border-slate-800 bg-slate-900/40 p-6">
        <h2 className="mb-1 text-sm font-semibold uppercase tracking-wide text-slate-300">
          Benchmark: asking multiple
        </h2>
        <p className="text-xs text-slate-500">
          No vertical benchmark is available for this deal yet. Benchmarks unlock once
          enough comparable deals have been processed in this vertical.
        </p>
      </div>
    )
  }
  const { p25, p50, p75, n_deals, source } = bm
  const claimed = Number(deal.claimed_sde)
  const askingMultiple = claimed > 0 ? Number(deal.asking_price) / claimed : NaN

  const min = Number(p25) * 0.7
  const max = Number(p75) * 1.3
  const pct = (v: number) => Math.min(100, Math.max(0, ((v - min) / (max - min)) * 100))

  return (
    <div className="rounded border border-slate-800 bg-slate-900/40 p-6">
      <h2 className="mb-1 text-sm font-semibold uppercase tracking-wide text-slate-300">
        Benchmark: asking multiple
      </h2>
      <p className="mb-6 text-xs text-slate-500">
        {source} &middot; n={n_deals} deals
      </p>

      <div className="relative mt-8 h-2 rounded-full bg-slate-800">
        <div
          className="absolute top-0 h-2 rounded-full bg-slate-600"
          style={{ left: `${pct(Number(p25))}%`, right: `${100 - pct(Number(p75))}%` }}
        />
        <div
          className="absolute -top-1 h-4 w-0.5 bg-slate-400"
          style={{ left: `${pct(Number(p50))}%` }}
        />
        {Number.isFinite(askingMultiple) && (
          <div
            className="absolute -top-2.5 flex flex-col items-center"
            style={{ left: `${pct(askingMultiple)}%`, transform: 'translateX(-50%)' }}
          >
            <div className="h-6 w-0.5 bg-signal-500" />
            <div className="mt-1 whitespace-nowrap rounded border border-signal-500/40 bg-signal-500/10 px-1.5 py-0.5 font-mono-num text-[10px] font-semibold text-signal-400">
              {formatMultiple(askingMultiple)} asking
            </div>
          </div>
        )}
      </div>

      <div className="mt-10 flex justify-between text-xs text-slate-500">
        <div>
          <div className="font-mono-num text-sm text-slate-300">{formatMultiple(p25)}</div>
          <div>p25</div>
        </div>
        <div className="text-center">
          <div className="font-mono-num text-sm text-slate-300">{formatMultiple(p50)}</div>
          <div>p50 (median)</div>
        </div>
        <div className="text-right">
          <div className="font-mono-num text-sm text-slate-300">{formatMultiple(p75)}</div>
          <div>p75</div>
        </div>
      </div>
    </div>
  )
}
