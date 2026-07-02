import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { TrianglePeriod } from '../types/report'
import { formatMoney, formatPct } from '../lib/format'

const COLORS = {
  tax: '#3987e5',
  pnl: '#199e70',
  bank: '#9085e9',
}

interface ChartRow {
  period: number
  'Tax return revenue': number
  'P&L revenue': number
  'Bank deposits': number
}

function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded border border-slate-700 bg-slate-900 px-3 py-2 text-xs shadow-xl">
      <p className="mb-1.5 font-semibold text-slate-200">{label}</p>
      {payload.map((entry: any) => (
        <div key={entry.name} className="flex items-center justify-between gap-4">
          <span className="flex items-center gap-1.5 text-slate-400">
            <span className="h-2 w-2 rounded-sm" style={{ backgroundColor: entry.color }} />
            {entry.name}
          </span>
          <span className="font-mono-num text-slate-100">{formatMoney(entry.value)}</span>
        </div>
      ))}
    </div>
  )
}

export default function TrianglePanel({ triangle }: { triangle: TrianglePeriod[] }) {
  const data: ChartRow[] = triangle.map((t) => ({
    period: t.period,
    'Tax return revenue': Number(t.tax_revenue),
    'P&L revenue': Number(t.pnl_revenue),
    'Bank deposits': Number(t.bank_deposits),
  }))

  return (
    <div className="rounded border border-slate-800 bg-slate-900/40 p-6">
      <div className="mb-1 flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-300">
          Triangle of Truth
        </h2>
      </div>
      <p className="mb-6 text-xs text-slate-500">
        Tax filings, P&amp;L, and bank deposits reconciled side by side, per period.
      </p>

      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 4, right: 8, left: 8, bottom: 4 }} barGap={2}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis dataKey="period" stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <YAxis
              stroke="#64748b"
              tick={{ fill: '#94a3b8', fontSize: 11 }}
              tickFormatter={(v) => `$${(v / 1000000).toFixed(1)}M`}
              width={56}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(148,163,184,0.06)' }} />
            <Legend wrapperStyle={{ fontSize: 12, color: '#94a3b8' }} />
            <Bar dataKey="Tax return revenue" fill={COLORS.tax} radius={[2, 2, 0, 0]} />
            <Bar dataKey="P&L revenue" fill={COLORS.pnl} radius={[2, 2, 0, 0]} />
            <Bar dataKey="Bank deposits" fill={COLORS.bank} radius={[2, 2, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-6 grid gap-3 sm:grid-cols-3">
        {triangle.map((t) => {
          const coverage = Number(t.deposit_coverage_pct)
          const divergence = Number(t.tax_vs_pnl_divergence_pct)
          const coverageBad = coverage < 92
          const divergenceBad = Math.abs(divergence) > 5
          return (
            <div
              key={t.period}
              className={`rounded border p-4 ${
                coverageBad || divergenceBad
                  ? 'border-signal-500/40 bg-signal-500/[0.06]'
                  : 'border-slate-800 bg-slate-950/40'
              }`}
            >
              <p className="font-mono-num text-sm font-semibold text-slate-200">{t.period}</p>
              <div className="mt-2 flex items-center justify-between text-xs">
                <span className="text-slate-500">Deposit coverage</span>
                <span
                  className={`font-mono-num font-semibold ${
                    coverageBad ? 'text-signal-500' : 'text-slate-300'
                  }`}
                >
                  {formatPct(t.deposit_coverage_pct)}
                </span>
              </div>
              <div className="mt-1 flex items-center justify-between text-xs">
                <span className="text-slate-500">Tax vs P&amp;L divergence</span>
                <span
                  className={`font-mono-num font-semibold ${
                    divergenceBad ? 'text-signal-500' : 'text-slate-300'
                  }`}
                >
                  {formatPct(t.tax_vs_pnl_divergence_pct)}
                </span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
