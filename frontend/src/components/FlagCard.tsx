import { useState } from 'react'
import type { Flag, ReportDocument } from '../types/report'
import SeverityChip from './SeverityChip'
import { useDocViewer } from '../context/DocViewerContext'
import { SEVERITY_CLASSES } from '../lib/severity'

type ReviewStatus = 'Resolved' | 'Accepted Risk' | 'Disputed' | null

function formatValue(v: string | number): string {
  if (typeof v === 'number') return String(v)
  const n = Number(v)
  if (!Number.isNaN(n) && v.trim() !== '' && /^-?\d+(\.\d+)?$/.test(v.trim())) {
    return n.toLocaleString('en-US', { maximumFractionDigits: 2 })
  }
  return v
}

export default function FlagCard({
  flag,
  documentsById,
}: {
  flag: Flag
  documentsById: Record<string, ReportDocument>
}) {
  const [open, setOpen] = useState(false)
  const [status, setStatus] = useState<ReviewStatus>(null)
  const { openDoc } = useDocViewer()
  const cls = SEVERITY_CLASSES[flag.severity]

  return (
    <div className={`rounded border-l-2 border border-slate-800 bg-slate-900/40 ${cls.border}`}>
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-start justify-between gap-4 px-5 py-4 text-left"
      >
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <SeverityChip severity={flag.severity} />
            <span className="text-[11px] font-mono-num uppercase tracking-wide text-slate-600">
              {flag.rule_id}
            </span>
            <span className="text-[11px] uppercase tracking-wide text-slate-600">{flag.category}</span>
            {status && (
              <span className="rounded border border-slate-600 bg-slate-800 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-slate-300">
                {status}
              </span>
            )}
          </div>
          <p className="mt-1.5 text-sm font-medium text-slate-100">{flag.title}</p>
          {!open && <p className="mt-0.5 truncate text-xs text-slate-500">{flag.detail}</p>}
        </div>
        <span className="mt-1 shrink-0 text-slate-500">{open ? '−' : '+'}</span>
      </button>

      {open && (
        <div className="space-y-5 border-t border-slate-800 px-5 py-5">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Finding</p>
            <p className="mt-1 text-sm text-slate-200">{flag.narrative.finding}</p>
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              Why it matters
            </p>
            <p className="mt-1 text-sm leading-relaxed text-slate-300">
              {flag.narrative.why_it_matters}
            </p>
          </div>

          {Object.keys(flag.computed_values).length > 0 && (
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                Computed values
              </p>
              <div className="overflow-hidden rounded border border-slate-800">
                <table className="w-full text-xs">
                  <tbody>
                    {Object.entries(flag.computed_values).map(([k, v], i) => (
                      <tr key={k} className={i % 2 === 0 ? 'bg-slate-950/40' : ''}>
                        <td className="px-3 py-1.5 capitalize text-slate-500">{k.replace(/_/g, ' ')}</td>
                        <td className="px-3 py-1.5 text-right font-mono-num text-slate-200">
                          {formatValue(v)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {flag.evidence_refs.length > 0 && (
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                Evidence
              </p>
              <div className="flex flex-wrap gap-2">
                {flag.evidence_refs.map((ref, i) => {
                  const doc = documentsById[ref.document_id]
                  return (
                    <button
                      key={`${ref.document_id}-${ref.page}-${i}`}
                      disabled={!doc}
                      onClick={() => doc && openDoc(doc, ref.page)}
                      className="rounded border border-slate-700 bg-slate-950/60 px-2.5 py-1.5 text-left text-xs text-slate-300 transition hover:border-slate-500 hover:text-slate-100 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      {ref.label} — <span className="font-mono-num">{ref.document_id} p{ref.page}</span>
                    </button>
                  )
                })}
              </div>
            </div>
          )}

          {flag.ask_seller.length > 0 && (
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                Ask the seller
              </p>
              <ul className="space-y-1.5">
                {flag.ask_seller.map((q, i) => (
                  <li key={i} className="flex gap-2 text-sm text-slate-300">
                    <span className="text-signal-500">&raquo;</span>
                    {q}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              What resolves this
            </p>
            <p className="mt-1 text-sm text-slate-300">{flag.what_resolves}</p>
          </div>

          <div className="border-t border-slate-800 pt-4">
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
              Buyer control
            </p>
            <div className="flex flex-wrap gap-2">
              {(['Resolved', 'Accepted Risk', 'Disputed'] as const).map((option) => (
                <button
                  key={option}
                  onClick={() => setStatus((s) => (s === option ? null : option))}
                  className={`rounded border px-3 py-1.5 text-xs font-medium transition ${
                    status === option
                      ? 'border-slate-400 bg-slate-700 text-slate-100'
                      : 'border-slate-700 text-slate-400 hover:border-slate-500 hover:text-slate-200'
                  }`}
                >
                  {option}
                </button>
              ))}
            </div>
            {status && (
              <p className="mt-2 text-xs italic text-slate-500">
                Marked "{status}" during post-review. This is a local annotation only — it is not sent
                anywhere in this demo.
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
