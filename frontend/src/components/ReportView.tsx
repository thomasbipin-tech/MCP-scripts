import { useMemo, type ReactNode } from 'react'
import ReportHeader from './ReportHeader'
import SeverityTiles from './SeverityTiles'
import ExecutiveSummary from './ExecutiveSummary'
import TrianglePanel from './TrianglePanel'
import FlagCard from './FlagCard'
import NormalizationTable from './NormalizationTable'
import BenchmarkPanel from './BenchmarkPanel'
import DataGaps from './DataGaps'
import SellerQuestionPack from './SellerQuestionPack'
import DisclaimerFooter from './DisclaimerFooter'
import WorkstreamsPanel from './WorkstreamsPanel'
import type { DealProofReport, ReportDocument, Verification } from '../types/report'

function SectionTitle({ children }: { children: ReactNode }) {
  return <h2 className="mb-4 text-base font-semibold text-slate-100">{children}</h2>
}

// How much to trust the figures: how many documents were analysed and how
// confidently the extraction read them. Green when reliable, amber when some
// documents came through low-confidence (their numbers are less certain).
function VerificationStrip({ v }: { v: Verification }) {
  const pct = Math.round(v.avg_confidence * 100)
  const ok = v.reliable
  return (
    <div
      className={`flex flex-wrap items-center gap-x-4 gap-y-1 rounded-lg border px-4 py-3 text-sm ${
        ok
          ? 'border-emerald-500/30 bg-emerald-500/[0.06] text-emerald-200'
          : 'border-amber-500/30 bg-amber-500/[0.06] text-amber-200'
      }`}
    >
      <span className="font-medium">
        {ok ? 'Figures verified against source documents' : 'Read these figures with caution'}
      </span>
      <span className="font-mono-num text-slate-300">
        {v.document_count} document{v.document_count === 1 ? '' : 's'} analysed · {pct}% avg extraction
        confidence
      </span>
      {v.low_confidence.length > 0 && (
        <span className="text-amber-300/90">
          {v.low_confidence.length} low-confidence:{' '}
          {v.low_confidence.map((d) => d.doc_type).join(', ')} — figures from these are less certain.
        </span>
      )}
    </div>
  )
}

// Presentational, self-contained render of a full DealProof report. Used by
// both the public static sample (/report, fed demo_report.json) and the
// per-deal workspace (fed the live API report) — the shape is identical.
export default function ReportView({ report }: { report: DealProofReport }) {
  const documentsById = useMemo<Record<string, ReportDocument>>(
    () => Object.fromEntries(report.documents.map((d) => [d.id, d])),
    [report],
  )

  return (
    <div className="flex min-h-full flex-col">
      <ReportHeader deal={report.deal} watermark={report.watermark} />

      <div className="mx-auto w-full max-w-6xl flex-1 space-y-10 px-4 py-8 sm:px-6">
        <section>
          <SeverityTiles counts={report.severity_counts} />
        </section>

        {report.verification && report.verification.document_count > 0 && (
          <VerificationStrip v={report.verification} />
        )}

        <section>
          <ExecutiveSummary items={report.executive_summary} />
        </section>

        <section>
          <TrianglePanel triangle={report.triangle} />
        </section>

        {report.workstreams && report.workstreams.length > 0 && (
          <section>
            <SectionTitle>Diligence workstreams</SectionTitle>
            <WorkstreamsPanel workstreams={report.workstreams} />
          </section>
        )}

        <section>
          <SectionTitle>Red flag ledger</SectionTitle>
          <div className="space-y-3">
            {report.flags.map((flag) => (
              <FlagCard key={flag.rule_id} flag={flag} documentsById={documentsById} />
            ))}
          </div>
        </section>

        <section>
          <NormalizationTable normalization={report.normalization} documentsById={documentsById} />
        </section>

        <section>
          <BenchmarkPanel benchmarks={report.benchmarks} deal={report.deal} />
        </section>

        <section>
          <DataGaps gaps={report.data_gaps} intro={report.narrative?.data_gaps_intro} />
        </section>

        <section>
          <SellerQuestionPack questions={report.seller_question_pack} />
        </section>
      </div>

      <DisclaimerFooter disclaimer={report.disclaimer} />
    </div>
  )
}
