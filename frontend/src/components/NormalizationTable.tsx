import type { Normalization } from '../types/report'
import { formatMoney } from '../lib/format'
import { useDocViewer } from '../context/DocViewerContext'
import type { ReportDocument } from '../types/report'

const VERDICT_CLASSES: Record<string, string> = {
  Verified: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
  Undocumented: 'bg-signal-500/10 text-signal-400 border-signal-500/30',
  Review: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
}

export default function NormalizationTable({
  normalization,
  documentsById,
}: {
  normalization: Normalization
  documentsById: Record<string, ReportDocument>
}) {
  const { openDoc } = useDocViewer()

  return (
    <div className="rounded border border-slate-800 bg-slate-900/40 p-6">
      <h2 className="mb-1 text-sm font-semibold uppercase tracking-wide text-slate-300">
        Financial normalization
      </h2>
      <p className="mb-5 text-xs text-slate-500">
        Add-backs to claimed SDE, verified against supporting documentation.
      </p>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[520px] text-sm">
          <thead>
            <tr className="border-b border-slate-800 text-left text-xs uppercase tracking-wide text-slate-500">
              <th className="pb-2 pr-3 font-medium">Description</th>
              <th className="pb-2 pr-3 text-right font-medium">Amount</th>
              <th className="pb-2 pr-3 font-medium">Verdict</th>
              <th className="pb-2 font-medium">Source</th>
            </tr>
          </thead>
          <tbody>
            {normalization.rows.map((row, i) => {
              const doc = documentsById[row.source.document_id]
              return (
                <tr key={i} className="border-b border-slate-800/60">
                  <td className="py-2.5 pr-3 text-slate-200">{row.description}</td>
                  <td className="py-2.5 pr-3 text-right font-mono-num text-slate-200">
                    {formatMoney(row.amount)}
                  </td>
                  <td className="py-2.5 pr-3">
                    <span
                      className={`inline-flex rounded border px-2 py-0.5 text-[11px] font-medium ${
                        VERDICT_CLASSES[row.verdict] ?? 'border-slate-700 text-slate-400'
                      }`}
                    >
                      {row.verdict}
                    </span>
                  </td>
                  <td className="py-2.5">
                    <button
                      disabled={!doc}
                      onClick={() => doc && openDoc(doc, row.source.page)}
                      className="text-xs text-slate-400 underline decoration-slate-700 underline-offset-2 transition hover:text-slate-200 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      {row.source.label}
                    </button>
                  </td>
                </tr>
              )
            })}
          </tbody>
          <tfoot>
            <tr className="border-t border-slate-700">
              <td className="pt-3 pr-3 text-sm font-semibold text-slate-200">Claimed SDE → Adjusted SDE</td>
              <td className="pt-3 pr-3 text-right font-mono-num text-sm font-semibold text-slate-100">
                {formatMoney(normalization.claimed_sde)} → {formatMoney(normalization.adjusted_sde)}
              </td>
              <td colSpan={2} />
            </tr>
          </tfoot>
        </table>
      </div>

      <p className="mt-4 border-t border-slate-800 pt-4 text-xs leading-relaxed text-slate-500">
        {normalization.note}
      </p>
    </div>
  )
}
