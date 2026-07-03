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
import type { DealProofReport, ReportDocument } from '../types/report'

function SectionTitle({ children }: { children: ReactNode }) {
  return <h2 className="mb-4 text-base font-semibold text-slate-100">{children}</h2>
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

        <section>
          <ExecutiveSummary items={report.executive_summary} />
        </section>

        <section>
          <TrianglePanel triangle={report.triangle} />
        </section>

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
