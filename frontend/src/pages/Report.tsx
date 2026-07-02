import { useEffect, useMemo, useState } from 'react'
import AppShell from '../components/AppShell'
import ReportHeader from '../components/ReportHeader'
import SeverityTiles from '../components/SeverityTiles'
import ExecutiveSummary from '../components/ExecutiveSummary'
import TrianglePanel from '../components/TrianglePanel'
import FlagCard from '../components/FlagCard'
import NormalizationTable from '../components/NormalizationTable'
import BenchmarkPanel from '../components/BenchmarkPanel'
import DataGaps from '../components/DataGaps'
import SellerQuestionPack from '../components/SellerQuestionPack'
import DisclaimerFooter from '../components/DisclaimerFooter'
import { loadDemoReport } from '../lib/loadReport'
import type { DealProofReport, ReportDocument } from '../types/report'

function SectionTitle({ children }: { children: React.ReactNode }) {
  return <h2 className="mb-4 text-base font-semibold text-slate-100">{children}</h2>
}

export default function Report() {
  const [report, setReport] = useState<DealProofReport | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    loadDemoReport()
      .then((r) => {
        if (!cancelled) setReport(r)
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Failed to load report')
      })
    return () => {
      cancelled = true
    }
  }, [])

  const documentsById = useMemo<Record<string, ReportDocument>>(() => {
    if (!report) return {}
    return Object.fromEntries(report.documents.map((d) => [d.id, d]))
  }, [report])

  if (error) {
    return (
      <AppShell title="Report">
        <div className="p-8 text-sm text-signal-400">Could not load report: {error}</div>
      </AppShell>
    )
  }

  if (!report) {
    return (
      <AppShell title="Report">
        <div className="p-8 text-sm text-slate-500">Loading report…</div>
      </AppShell>
    )
  }

  return (
    <AppShell title="Report">
      <div className="flex min-h-full flex-col">
        <ReportHeader deal={report.deal} watermark={report.watermark} />

        <div className="mx-auto w-full max-w-6xl flex-1 space-y-10 px-6 py-8">
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
    </AppShell>
  )
}
