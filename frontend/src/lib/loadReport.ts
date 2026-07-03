import type { DealProofReport } from '../types/report'

// Resolve a public asset against the app's base URL so it works both at the
// site root (dev / server deploy) and under a GitHub Pages project subpath.
export function asset(path: string): string {
  return import.meta.env.BASE_URL + path.replace(/^\//, '')
}

export async function loadDemoReport(): Promise<DealProofReport> {
  const res = await fetch(asset('demo_report.json'))
  if (!res.ok) {
    throw new Error(`Failed to load demo report: ${res.status}`)
  }
  return (await res.json()) as DealProofReport
}
