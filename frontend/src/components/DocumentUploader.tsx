import { useRef, useState, type DragEvent } from 'react'

export default function DocumentUploader({
  onFiles,
  disabled,
}: {
  onFiles: (files: File[]) => void
  disabled?: boolean
}) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)

  function handleFiles(fileList: FileList | null) {
    if (!fileList || fileList.length === 0) return
    const files = Array.from(fileList).filter(
      (f) => f.type === 'application/pdf' || f.name.toLowerCase().endsWith('.pdf'),
    )
    if (files.length > 0) onFiles(files)
  }

  function handleDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault()
    setDragging(false)
    if (disabled) return
    handleFiles(e.dataTransfer.files)
  }

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault()
        if (!disabled) setDragging(true)
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      onClick={() => !disabled && inputRef.current?.click()}
      role="button"
      tabIndex={disabled ? -1 : 0}
      className={`flex cursor-pointer flex-col items-center justify-center rounded border-2 border-dashed px-4 py-8 text-center transition ${
        disabled
          ? 'cursor-not-allowed border-slate-800 opacity-50'
          : dragging
            ? 'border-signal-500 bg-signal-500/5'
            : 'border-slate-700 hover:border-slate-500'
      }`}
    >
      <p className="text-sm font-medium text-slate-200">Drop PDFs here, or tap to browse</p>
      <p className="mt-1 text-xs text-slate-500">Tax returns, P&amp;Ls, bank statements, leases, contracts…</p>
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf"
        multiple
        disabled={disabled}
        className="hidden"
        onChange={(e) => {
          handleFiles(e.target.files)
          e.target.value = ''
        }}
      />
    </div>
  )
}
