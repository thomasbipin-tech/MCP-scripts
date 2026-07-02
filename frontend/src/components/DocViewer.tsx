import { useDocViewer } from '../context/DocViewerContext'

export default function DocViewer() {
  const { document: doc, page, close } = useDocViewer()

  if (!doc) return null

  return (
    <div className="fixed inset-0 z-50 flex justify-end no-print" role="dialog" aria-modal="true">
      <div className="absolute inset-0 bg-slate-950/70 backdrop-blur-sm" onClick={close} />
      <div className="relative flex h-full w-full max-w-3xl flex-col border-l border-slate-800 bg-slate-900 shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-800 px-5 py-4">
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-slate-100">{doc.title}</p>
            <p className="mt-0.5 font-mono-num text-xs text-slate-400">
              page {page} of {doc.page_count} &middot; {doc.doc_type}
            </p>
          </div>
          <button
            onClick={close}
            className="ml-4 shrink-0 rounded border border-slate-700 px-2.5 py-1.5 text-xs text-slate-300 transition hover:border-slate-500 hover:text-slate-100"
          >
            Close
          </button>
        </div>
        <div className="flex-1 bg-slate-950">
          <iframe
            key={`${doc.id}-${page}`}
            title={doc.title}
            src={`${doc.url}#page=${page}`}
            className="h-full w-full"
          />
        </div>
      </div>
    </div>
  )
}
