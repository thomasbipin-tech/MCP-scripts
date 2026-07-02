const STAGE_CLASSES: Record<string, string> = {
  Uploading: 'bg-slate-700/40 text-slate-300 border-slate-600',
  Processing: 'bg-blue-400/10 text-blue-300 border-blue-400/30',
  'In Review': 'bg-amber-500/10 text-amber-400 border-amber-500/30',
  'Report Ready': 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
  Archived: 'bg-slate-800 text-slate-500 border-slate-700',
}

export default function StageBadge({ stage }: { stage: string }) {
  const cls = STAGE_CLASSES[stage] ?? 'bg-slate-700/40 text-slate-300 border-slate-600'
  return (
    <span className={`inline-flex items-center rounded border px-2 py-0.5 text-[11px] font-medium ${cls}`}>
      {stage}
    </span>
  )
}
