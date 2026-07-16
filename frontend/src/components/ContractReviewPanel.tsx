import type { ClauseFinding, ContractReview, ReportDocument } from '../types/report'
import SeverityChip from './SeverityChip'
import { useDocViewer } from '../context/DocViewerContext'
import { SEVERITY_CLASSES } from '../lib/severity'

function docTypeLabel(t: string): string {
  return t.replace('contract_', '').replace(/_/g, ' ')
}

function ClauseRow({
  clause,
  documentsById,
}: {
  clause: ClauseFinding
  documentsById: Record<string, ReportDocument>
}) {
  const { openDoc } = useDocViewer()
  const cls = SEVERITY_CLASSES[clause.severity]
  const doc = documentsById[clause.source.document_id]
  return (
    <div className={`rounded border border-l-2 border-slate-800 bg-slate-950/40 ${cls.border} p-3`}>
      <div className="flex flex-wrap items-center gap-2">
        <SeverityChip severity={clause.severity} />
        <span className="text-sm font-medium text-slate-100">{clause.label}</span>
      </div>
      {/* The contract's own words — grounded, never paraphrased by an LLM. */}
      <blockquote className="mt-2 border-l-2 border-slate-700 pl-3 text-xs italic text-slate-300">
        “{clause.quote}”
      </blockquote>
      <p className="mt-2 text-xs leading-relaxed text-slate-400">
        <span className="font-semibold text-slate-300">Why it matters. </span>
        {clause.risk}
      </p>
      <p className="mt-1 text-xs leading-relaxed text-slate-400">
        <span className="font-semibold text-slate-300">Do this. </span>
        {clause.buyer_action}
      </p>
      <button
        onClick={() => doc && openDoc(doc, clause.source.page)}
        disabled={!doc}
        className="mt-2 text-[11px] font-medium text-[#4cc0b4] hover:underline disabled:text-slate-600 disabled:no-underline"
      >
        Source: {clause.source.label} · p{clause.source.page}
      </button>
    </div>
  )
}

export default function ContractReviewPanel({
  review,
  documentsById,
}: {
  review: ContractReview
  documentsById: Record<string, ReportDocument>
}) {
  return (
    <div>
      <p className="mb-4 text-sm text-slate-400">
        A deterministic scan of every contract and lease in the data room — {review.clauses_flagged} clause
        risk{review.clauses_flagged === 1 ? '' : 's'} across {review.documents_reviewed} document
        {review.documents_reviewed === 1 ? '' : 's'}. Each item quotes the contract and links to the page,
        so your attorney can verify it in seconds.
      </p>

      <div className="space-y-4">
        {review.contracts.map((c) => (
          <div key={c.document_id} className="rounded-xl border border-slate-800 bg-slate-900/40 p-4">
            <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
              <div className="min-w-0">
                <h3 className="truncate text-sm font-semibold text-slate-100">{c.counterparty}</h3>
                <p className="text-[11px] uppercase tracking-wide text-slate-500">
                  {docTypeLabel(c.doc_type)}
                </p>
              </div>
              <SeverityChip severity={c.highest_severity} />
            </div>
            <div className="space-y-2">
              {c.findings.map((f, i) => (
                <ClauseRow key={`${f.clause_type}-${i}`} clause={f} documentsById={documentsById} />
              ))}
            </div>
          </div>
        ))}
      </div>

      <p className="mt-3 text-[11px] leading-relaxed text-slate-600">{review.note}</p>
    </div>
  )
}
