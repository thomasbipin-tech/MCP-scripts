import type { DealProofReport } from '../types/report'

export async function loadDemoReport(): Promise<DealProofReport> {
  const res = await fetch('/demo_report.json')
  if (!res.ok) {
    throw new Error(`Failed to load demo report: ${res.status}`)
  }
  return (await res.json()) as DealProofReport
}
