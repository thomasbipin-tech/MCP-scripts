import { useEffect, useState } from 'react'
import AppShell from '../components/AppShell'
import DealCard, { type DealCardData } from '../components/DealCard'
import { loadDemoReport } from '../lib/loadReport'

const PLACEHOLDER_DEALS: DealCardData[] = [
  {
    codename: 'Project Anchor',
    vertical_label: 'Commercial Landscaping',
    asking_price: '890000',
    stage: 'Uploading',
    severity_counts: { CRITICAL: 0, HIGH: 0, MEDIUM: 0, INFO: 0 },
  },
  {
    codename: 'Project Bluefin',
    vertical_label: 'Coin-Op Laundromat',
    asking_price: '410000',
    stage: 'Processing',
    severity_counts: { CRITICAL: 0, HIGH: 0, MEDIUM: 0, INFO: 0 },
  },
  {
    codename: 'Project Cascade',
    vertical_label: 'Self-Storage Facility',
    asking_price: '2350000',
    stage: 'In Review',
    severity_counts: { CRITICAL: 1, HIGH: 3, MEDIUM: 2, INFO: 2 },
  },
]

function NewDealModal({ onClose }: { onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-slate-950/70 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-md rounded border border-slate-700 bg-slate-900 p-6">
        <h2 className="text-sm font-semibold text-slate-100">Start a new deal</h2>
        <p className="mt-2 text-sm text-slate-400">
          Data-room upload is not wired up in this demo workspace. In production this opens an intake
          flow that collects the seller's documents and kicks off the Triangle of Truth reconciliation.
        </p>
        <button
          onClick={onClose}
          className="mt-6 rounded border border-slate-700 px-4 py-2 text-sm text-slate-200 hover:border-slate-500"
        >
          Close
        </button>
      </div>
    </div>
  )
}

export default function Deals() {
  const [demoDeal, setDemoDeal] = useState<DealCardData | null>(null)
  const [modalOpen, setModalOpen] = useState(false)

  useEffect(() => {
    let cancelled = false
    loadDemoReport()
      .then((report) => {
        if (cancelled) return
        setDemoDeal({
          codename: report.deal.codename,
          vertical_label: report.deal.vertical_label,
          asking_price: report.deal.asking_price,
          stage: report.deal.stage,
          severity_counts: report.severity_counts,
          linkTo: '/report',
        })
      })
      .catch(() => setDemoDeal(null))
    return () => {
      cancelled = true
    }
  }, [])

  const deals = demoDeal ? [demoDeal, ...PLACEHOLDER_DEALS] : PLACEHOLDER_DEALS

  return (
    <AppShell title="Deals">
      <div className="mx-auto max-w-6xl px-6 py-8">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-100">Deal dashboard</h2>
            <p className="mt-1 text-sm text-slate-500">All active and archived diligence engagements.</p>
          </div>
          <button
            onClick={() => setModalOpen(true)}
            className="rounded bg-signal-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-signal-600"
          >
            New Deal
          </button>
        </div>

        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {deals.map((deal) => (
            <DealCard key={deal.codename} deal={deal} />
          ))}
        </div>
      </div>
      {modalOpen && <NewDealModal onClose={() => setModalOpen(false)} />}
    </AppShell>
  )
}
