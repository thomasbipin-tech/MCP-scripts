import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import AppShell from '../components/AppShell'
import DealCard, { type DealCardData } from '../components/DealCard'
import { apiGet, apiPost } from '../lib/api'
import { VERTICAL_OPTIONS, verticalLabel } from '../lib/vertical'
import type { DealCreatePayload, DealSummary } from '../types/api'

function dealToCard(deal: DealSummary): DealCardData {
  return {
    codename: deal.codename,
    vertical_label: verticalLabel(deal.vertical),
    asking_price: deal.asking_price ?? '',
    stage: deal.stage,
    severity_counts: deal.severity_counts,
    linkTo: `/deals/${deal.id}`,
  }
}

function NewDealModal({
  onClose,
  onCreated,
}: {
  onClose: () => void
  onCreated: (deal: DealSummary) => void
}) {
  const [codename, setCodename] = useState('')
  const [entityName, setEntityName] = useState('')
  const [vertical, setVertical] = useState(VERTICAL_OPTIONS[0].value)
  const [state, setState] = useState('')
  const [askingPrice, setAskingPrice] = useState('')
  const [claimedSde, setClaimedSde] = useState('')
  const [dealType, setDealType] = useState<'asset' | 'stock'>('asset')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!codename.trim()) return
    setSubmitting(true)
    setError(null)
    try {
      const payload: DealCreatePayload = {
        codename: codename.trim(),
        vertical,
        deal_type: dealType,
      }
      if (entityName.trim()) payload.entity_name = entityName.trim()
      if (state.trim()) payload.state = state.trim()
      if (askingPrice.trim()) payload.asking_price = askingPrice.trim()
      if (claimedSde.trim()) payload.claimed_sde = claimedSde.trim()
      const deal = await apiPost<DealSummary>('/deals', payload)
      onCreated(deal)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create deal')
      setSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
      <div className="absolute inset-0 bg-slate-950/70 backdrop-blur-sm" onClick={onClose} />
      <div className="relative max-h-[90vh] w-full max-w-md overflow-y-auto rounded border border-slate-700 bg-slate-900 p-6">
        <h2 className="text-sm font-semibold text-slate-100">Start a new deal</h2>
        <p className="mt-1 text-xs text-slate-500">
          Create the deal shell, then upload the data room from the deal workspace.
        </p>

        <form onSubmit={handleSubmit} className="mt-5 space-y-4">
          <label className="block">
            <span className="mb-1.5 block text-xs font-medium uppercase tracking-wide text-slate-500">
              Codename *
            </span>
            <input
              required
              value={codename}
              onChange={(e) => setCodename(e.target.value)}
              placeholder="Project Anchor"
              className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-slate-500"
            />
          </label>

          <label className="block">
            <span className="mb-1.5 block text-xs font-medium uppercase tracking-wide text-slate-500">
              Entity name
            </span>
            <input
              value={entityName}
              onChange={(e) => setEntityName(e.target.value)}
              placeholder="Anchor Services LLC"
              className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-slate-500"
            />
          </label>

          <div className="grid grid-cols-2 gap-3">
            <label className="block">
              <span className="mb-1.5 block text-xs font-medium uppercase tracking-wide text-slate-500">
                Vertical *
              </span>
              <select
                value={vertical}
                onChange={(e) => setVertical(e.target.value)}
                className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-slate-500"
              >
                {VERTICAL_OPTIONS.map((v) => (
                  <option key={v.value} value={v.value}>
                    {v.label}
                  </option>
                ))}
              </select>
            </label>

            <label className="block">
              <span className="mb-1.5 block text-xs font-medium uppercase tracking-wide text-slate-500">
                State
              </span>
              <input
                value={state}
                onChange={(e) => setState(e.target.value.toUpperCase())}
                placeholder="OH"
                maxLength={2}
                className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-slate-500"
              />
            </label>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <label className="block">
              <span className="mb-1.5 block text-xs font-medium uppercase tracking-wide text-slate-500">
                Asking price
              </span>
              <input
                inputMode="numeric"
                value={askingPrice}
                onChange={(e) => setAskingPrice(e.target.value.replace(/[^0-9.]/g, ''))}
                placeholder="1560000"
                className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-slate-500"
              />
            </label>

            <label className="block">
              <span className="mb-1.5 block text-xs font-medium uppercase tracking-wide text-slate-500">
                Claimed SDE
              </span>
              <input
                inputMode="numeric"
                value={claimedSde}
                onChange={(e) => setClaimedSde(e.target.value.replace(/[^0-9.]/g, ''))}
                placeholder="520000"
                className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-slate-500"
              />
            </label>
          </div>

          <label className="block">
            <span className="mb-1.5 block text-xs font-medium uppercase tracking-wide text-slate-500">
              Deal type
            </span>
            <select
              value={dealType}
              onChange={(e) => setDealType(e.target.value as 'asset' | 'stock')}
              className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-slate-500"
            >
              <option value="asset">Asset</option>
              <option value="stock">Stock</option>
            </select>
          </label>

          {error && <p className="text-xs text-signal-400">{error}</p>}

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded border border-slate-700 px-4 py-2 text-sm text-slate-200 hover:border-slate-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="rounded bg-signal-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-signal-600 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {submitting ? 'Creating…' : 'Create deal'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function Deals() {
  const [deals, setDeals] = useState<DealSummary[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [modalOpen, setModalOpen] = useState(false)
  const navigate = useNavigate()

  const load = useCallback(() => {
    setError(null)
    apiGet<DealSummary[]>('/deals')
      .then(setDeals)
      .catch((e) => setError(e instanceof Error ? e.message : 'Failed to load deals'))
  }, [])

  useEffect(() => {
    load()
  }, [load])

  function handleCreated(deal: DealSummary) {
    setModalOpen(false)
    navigate(`/deals/${deal.id}`)
  }

  return (
    <AppShell title="Deals">
      <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
        <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
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

        {error && (
          <div className="mb-6 rounded border border-signal-500/30 bg-signal-500/10 p-4 text-sm text-signal-400">
            {error}
          </div>
        )}

        {deals === null && !error && <p className="text-sm text-slate-500">Loading deals…</p>}

        {deals !== null && deals.length === 0 && (
          <div className="rounded border border-dashed border-slate-700 bg-slate-900/20 p-10 text-center">
            <p className="text-sm text-slate-300">No deals yet.</p>
            <p className="mt-1 text-xs text-slate-500">
              Start your first diligence engagement to upload a data room and generate a report.
            </p>
            <button
              onClick={() => setModalOpen(true)}
              className="mt-5 rounded bg-signal-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-signal-600"
            >
              New Deal
            </button>
          </div>
        )}

        {deals !== null && deals.length > 0 && (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {deals.map((deal) => (
              <DealCard key={deal.id} deal={dealToCard(deal)} />
            ))}
          </div>
        )}
      </div>
      {modalOpen && <NewDealModal onClose={() => setModalOpen(false)} onCreated={handleCreated} />}
    </AppShell>
  )
}
