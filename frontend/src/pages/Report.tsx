import { useEffect, useState } from 'react'
import AppShell from '../components/AppShell'
import ReportView from '../components/ReportView'
import { loadDemoReport } from '../lib/loadReport'
import type { DealProofReport } from '../types/report'

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
      <ReportView report={report} />
    </AppShell>
  )
}
