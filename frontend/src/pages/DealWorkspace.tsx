import { useCallback, useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import AppShell from '../components/AppShell'
import DocumentUploader from '../components/DocumentUploader'
import ReportView from '../components/ReportView'
import SeverityTiles from '../components/SeverityTiles'
import StageBadge from '../components/StageBadge'
import { apiGet, apiGetBlob, apiPost, apiPostForm, ApiError } from '../lib/api'
import { formatMoney } from '../lib/format'
import { verticalLabel } from '../lib/vertical'
import { useAuth } from '../context/AuthContext'
import {
  isUploadDuplicate,
  type CheckoutResult,
  type DealSummary,
  type DocumentInfo,
  type ProcessResult,
  type PublishResult,
  type ReportResponse,
  type UploadResult,
  type WebhookResult,
} from '../types/api'

const DOC_TYPE_OPTIONS = [
  'tax_return_1120S',
  'tax_return_1065',
  'tax_return_schedule_c',
  'pnl',
  'balance_sheet',
  'bank_statement',
  'ar_aging',
  'addbacks',
  'contract_customer',
  'contract_supplier',
  'lease',
  'other',
]

function docTypeLabel(t: string): string {
  return t.replace(/_/g, ' ')
}

export default function DealWorkspace() {
  const { id } = useParams<{ id: string }>()
  const { user } = useAuth()

  const [deal, setDeal] = useState<DealSummary | null>(null)
  const [dealError, setDealError] = useState<string | null>(null)

  const [documents, setDocuments] = useState<DocumentInfo[] | null>(null)
  const [docsError, setDocsError] = useState<string | null>(null)

  const [uploadNotices, setUploadNotices] = useState<string[]>([])
  const [uploading, setUploading] = useState(false)

  const [processing, setProcessing] = useState(false)
  const [processError, setProcessError] = useState<string | null>(null)

  const [reportResp, setReportResp] = useState<ReportResponse | null>(null)
  const [reportChecked, setReportChecked] = useState(false)
  const [reportError, setReportError] = useState<string | null>(null)

  const [publishing, setPublishing] = useState(false)
  const [publishError, setPublishError] = useState<string | null>(null)

  const [paying, setPaying] = useState(false)
  const [payError, setPayError] = useState<string | null>(null)

  const [downloading, setDownloading] = useState(false)
  const [downloadError, setDownloadError] = useState<string | null>(null)

  const loadDeal = useCallback(async () => {
    if (!id) return
    try {
      const d = await apiGet<DealSummary>(`/deals/${id}`)
      setDeal(d)
      setDealError(null)
    } catch (e) {
      setDealError(e instanceof Error ? e.message : 'Failed to load deal')
    }
  }, [id])

  const loadDocuments = useCallback(async () => {
    if (!id) return
    try {
      const docs = await apiGet<DocumentInfo[]>(`/deals/${id}/documents`)
      setDocuments(docs)
      setDocsError(null)
    } catch (e) {
      setDocsError(e instanceof Error ? e.message : 'Failed to load documents')
    }
  }, [id])

  const loadReport = useCallback(async () => {
    if (!id) return
    setReportError(null)
    try {
      const resp = await apiGet<ReportResponse>(`/deals/${id}/report`)
      setReportResp(resp)
    } catch (e) {
      if (e instanceof ApiError && e.status === 409) {
        setReportResp(null)
      } else {
        setReportError(e instanceof Error ? e.message : 'Failed to load report')
      }
    } finally {
      setReportChecked(true)
    }
  }, [id])

  useEffect(() => {
    setDeal(null)
    setDocuments(null)
    setReportResp(null)
    setReportChecked(false)
    loadDeal()
    loadDocuments()
  }, [loadDeal, loadDocuments])

  // A processed-but-unpublished report 409s, so it's safe to poke this any
  // time the deal has left the "Uploading" stage.
  useEffect(() => {
    if (!deal) return
    if (deal.stage !== 'Uploading') {
      loadReport()
    } else {
      setReportChecked(true)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [deal?.stage, deal?.report_published, deal?.paid, loadReport])

  async function handleUpload(files: File[]) {
    if (!id) return
    setUploading(true)
    const notices: string[] = []
    for (const file of files) {
      try {
        const form = new FormData()
        form.append('file', file)
        const result = await apiPostForm<UploadResult>(`/deals/${id}/documents`, form)
        if (isUploadDuplicate(result)) {
          notices.push(`${file.name}: duplicate skipped`)
        }
      } catch (e) {
        notices.push(`${file.name}: ${e instanceof Error ? e.message : 'upload failed'}`)
      }
    }
    setUploadNotices(notices)
    setUploading(false)
    await loadDocuments()
  }

  async function handleReclassify(docId: string, docType: string) {
    if (!id) return
    try {
      await apiPost(`/deals/${id}/documents/${docId}/reclassify?doc_type=${encodeURIComponent(docType)}`)
      await loadDocuments()
    } catch (e) {
      setDocsError(e instanceof Error ? e.message : 'Failed to reclassify document')
    }
  }

  async function handleProcess() {
    if (!id) return
    setProcessing(true)
    setProcessError(null)
    try {
      await apiPost<ProcessResult>(`/deals/${id}/process`)
      await loadDeal()
      await loadDocuments()
      await loadReport()
    } catch (e) {
      setProcessError(e instanceof Error ? e.message : 'Processing failed')
    } finally {
      setProcessing(false)
    }
  }

  async function handlePublish() {
    if (!id) return
    setPublishing(true)
    setPublishError(null)
    try {
      await apiPost<PublishResult>(`/admin/deals/${id}/publish`)
      await loadDeal()
      await loadReport()
    } catch (e) {
      setPublishError(e instanceof Error ? e.message : 'Publish failed')
    } finally {
      setPublishing(false)
    }
  }

  async function handleUnlock() {
    if (!id) return
    setPaying(true)
    setPayError(null)
    try {
      const checkout = await apiPost<CheckoutResult>(`/payments/deals/${id}/checkout`, {
        tier: 'Full Diligence Report',
      })
      const match = checkout.checkout_url.match(/payment_id=([^&]+)/)
      const paymentId = match?.[1]
      if (!paymentId) throw new Error('Could not determine payment id from checkout response')
      await apiPost<WebhookResult>('/payments/webhook', { payment_id: paymentId })
      await loadDeal()
      await loadReport()
    } catch (e) {
      setPayError(e instanceof Error ? e.message : 'Payment failed')
    } finally {
      setPaying(false)
    }
  }

  async function handleDownloadPdf() {
    if (!id || !deal) return
    setDownloading(true)
    setDownloadError(null)
    try {
      const blob = await apiGetBlob(`/deals/${id}/report.pdf`)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `dealproof-${deal.codename}.pdf`
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(url)
    } catch (e) {
      setDownloadError(e instanceof Error ? e.message : 'Download failed')
    } finally {
      setDownloading(false)
    }
  }

  if (dealError) {
    return (
      <AppShell title="Deal">
        <div className="p-8 text-sm text-signal-400">{dealError}</div>
      </AppShell>
    )
  }

  if (!deal) {
    return (
      <AppShell title="Deal">
        <div className="p-8 text-sm text-slate-500">Loading deal…</div>
      </AppShell>
    )
  }

  const processed = deal.stage !== 'Uploading'
  const noDocs = documents !== null && documents.length === 0
  const canProcess = (documents?.length ?? 0) > 0 && !processing
  const lockedResp = reportResp && reportResp.locked ? reportResp : null
  const unlockedResp = reportResp && !reportResp.locked ? reportResp : null

  return (
    <AppShell title={deal.codename}>
      <div className="mx-auto max-w-6xl space-y-8 px-4 py-8 sm:px-6">
        {/* Header */}
        <div className="rounded border border-slate-800 bg-slate-900/40 p-5 sm:p-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="min-w-0">
              <h1 className="truncate text-xl font-bold text-slate-50">{deal.codename}</h1>
              <p className="mt-1 text-sm text-slate-500">{deal.entity_name ?? '—'}</p>
              <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-slate-500">
                <span className="rounded border border-slate-700 px-2 py-0.5">
                  {verticalLabel(deal.vertical)}
                </span>
                {deal.state && (
                  <span className="rounded border border-slate-700 px-2 py-0.5">{deal.state}</span>
                )}
                <span className="rounded border border-slate-700 px-2 py-0.5 capitalize">
                  {deal.deal_type} deal
                </span>
                <StageBadge stage={deal.stage} />
              </div>
            </div>
            <div className="text-right">
              <div className="font-mono-num text-2xl font-bold text-slate-50">
                {formatMoney(deal.asking_price)}
              </div>
              <p className="text-xs uppercase tracking-wide text-slate-500">Asking price</p>
            </div>
          </div>
        </div>

        {/* Documents */}
        <section className="rounded border border-slate-800 bg-slate-900/40 p-5 sm:p-6">
          <h2 className="mb-1 text-sm font-semibold uppercase tracking-wide text-slate-300">Documents</h2>
          <p className="mb-4 text-xs text-slate-500">
            Upload the data room. We classify each file automatically — override below if needed.
          </p>

          <DocumentUploader onFiles={handleUpload} disabled={uploading} />
          {uploading && <p className="mt-2 text-xs text-slate-500">Uploading…</p>}
          {uploadNotices.length > 0 && (
            <ul className="mt-2 space-y-1">
              {uploadNotices.map((n, i) => (
                <li key={i} className="text-xs text-amber-400">
                  {n}
                </li>
              ))}
            </ul>
          )}

          <div className="mt-5">
            {docsError && <p className="text-xs text-signal-400">{docsError}</p>}
            {documents === null && !docsError && <p className="text-xs text-slate-500">Loading documents…</p>}
            {noDocs && <p className="text-xs text-slate-500">No documents uploaded yet.</p>}
            {documents !== null && documents.length > 0 && (
              <div className="space-y-2">
                {documents.map((doc) => (
                  <div
                    key={doc.id}
                    className="flex flex-col gap-2 rounded border border-slate-800 bg-slate-950/40 p-3 sm:flex-row sm:items-center sm:justify-between"
                  >
                    <div className="min-w-0 text-xs text-slate-400">
                      <p className="truncate font-mono-num text-slate-200">{doc.id}</p>
                      <p className="mt-0.5">
                        {doc.entity_name ?? 'Unknown entity'} &middot; {doc.page_count} pg
                        {doc.confidence != null && <> &middot; {(doc.confidence * 100).toFixed(0)}% confidence</>}
                      </p>
                    </div>
                    <select
                      value={doc.doc_type}
                      onChange={(e) => handleReclassify(doc.id, e.target.value)}
                      className="w-full rounded border border-slate-700 bg-slate-950 px-2 py-1.5 text-xs text-slate-200 outline-none focus:border-slate-500 sm:w-56"
                    >
                      {DOC_TYPE_OPTIONS.map((t) => (
                        <option key={t} value={t}>
                          {docTypeLabel(t)}
                        </option>
                      ))}
                    </select>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="mt-5 border-t border-slate-800 pt-5">
            <button
              onClick={handleProcess}
              disabled={!canProcess}
              className="rounded bg-signal-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-signal-600 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {processing ? 'Processing…' : 'Process documents'}
            </button>
            {noDocs && <p className="mt-2 text-xs text-slate-600">Upload at least one document to process.</p>}
            {processError && <p className="mt-2 text-xs text-signal-400">{processError}</p>}
          </div>
        </section>

        {/* Report */}
        <section className="rounded border border-slate-800 bg-slate-900/40 p-5 sm:p-6">
          <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-300">Report</h2>

          {!processed && (
            <p className="text-sm text-slate-400">Process the documents to generate the report.</p>
          )}

          {processed && !reportChecked && <p className="text-sm text-slate-500">Loading report…</p>}

          {processed && reportChecked && !deal.report_published && (
            <div className="space-y-4">
              <SeverityTiles counts={deal.severity_counts} />
              <div className="rounded border border-amber-500/30 bg-amber-500/10 p-4 text-sm text-amber-300">
                Report generated — awaiting admin publish.
              </div>
              {user?.role === 'admin' ? (
                <div>
                  <button
                    onClick={handlePublish}
                    disabled={publishing}
                    className="rounded bg-signal-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-signal-600 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {publishing ? 'Publishing…' : 'Publish report'}
                  </button>
                  {publishError && <p className="mt-2 text-xs text-signal-400">{publishError}</p>}
                </div>
              ) : (
                <p className="text-xs text-slate-500">
                  An admin must publish this report before it can be unlocked.
                </p>
              )}
            </div>
          )}

          {processed && reportChecked && deal.report_published && reportError && (
            <p className="text-sm text-signal-400">{reportError}</p>
          )}

          {processed && reportChecked && deal.report_published && !reportError && lockedResp && (
            <div className="space-y-5">
              <SeverityTiles counts={lockedResp.severity_counts} />
              <div className="relative overflow-hidden rounded border border-slate-800">
                <div className="pointer-events-none select-none space-y-4 p-6 blur-sm" aria-hidden="true">
                  <div className="h-4 w-2/3 rounded bg-slate-700" />
                  <div className="h-4 w-full rounded bg-slate-800" />
                  <div className="h-4 w-5/6 rounded bg-slate-800" />
                  <div className="h-24 w-full rounded bg-slate-800" />
                </div>
                <div className="absolute inset-0 flex items-center justify-center bg-slate-950/70 p-6">
                  <div className="text-center">
                    <p className="mb-3 text-sm text-slate-300">Report locked — payment required.</p>
                    <button
                      onClick={handleUnlock}
                      disabled={paying}
                      className="rounded bg-signal-500 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-signal-600 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {paying ? 'Unlocking…' : 'Unlock — pay'}
                    </button>
                    {payError && <p className="mt-2 text-xs text-signal-400">{payError}</p>}
                  </div>
                </div>
              </div>
            </div>
          )}

          {processed && reportChecked && deal.report_published && !reportError && unlockedResp && (
            <div className="space-y-4">
              <div className="flex justify-end">
                <button
                  onClick={handleDownloadPdf}
                  disabled={downloading}
                  className="rounded border border-slate-700 px-4 py-2 text-xs font-medium text-slate-200 transition hover:border-slate-500 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {downloading ? 'Preparing…' : 'Download PDF'}
                </button>
              </div>
              {downloadError && <p className="text-right text-xs text-signal-400">{downloadError}</p>}
              <div className="-mx-5 -mb-5 rounded border border-slate-800 sm:-mx-6 sm:-mb-6">
                <ReportView report={unlockedResp.report} />
              </div>
            </div>
          )}
        </section>
      </div>
    </AppShell>
  )
}
