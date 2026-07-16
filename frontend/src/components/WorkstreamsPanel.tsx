import type { Workstream } from '../types/report'
import { formatMoney, formatPct } from '../lib/format'

const COVERAGE_STYLE: Record<Workstream['coverage'], string> = {
  automated: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300',
  partial: 'border-amber-500/30 bg-amber-500/10 text-amber-300',
  guided: 'border-slate-600/50 bg-slate-700/20 text-slate-300',
  roadmap: 'border-sky-500/30 bg-sky-500/10 text-sky-300',
}

const COVERAGE_SHORT: Record<Workstream['coverage'], string> = {
  automated: 'Automated',
  partial: 'Part-automated',
  guided: 'Checklist',
  roadmap: 'Roadmap',
}

function WorkstreamCard({ w }: { w: Workstream }) {
  return (
    <details className="group rounded-xl border border-slate-800 bg-slate-900/40 [&_summary]:cursor-pointer">
      <summary className="flex list-none items-start justify-between gap-3 p-4">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-slate-100">{w.title}</h3>
            {w.finding_count > 0 && (
              <span className="rounded-full bg-signal-500/15 px-2 py-0.5 font-mono-num text-[11px] font-semibold text-signal-400">
                {w.finding_count} finding{w.finding_count === 1 ? '' : 's'}
              </span>
            )}
          </div>
          <p className="mt-1 text-xs leading-relaxed text-slate-400">{w.description}</p>
        </div>
        <span
          className={`shrink-0 rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${COVERAGE_STYLE[w.coverage]}`}
        >
          {COVERAGE_SHORT[w.coverage]}
        </span>
      </summary>

      <div className="space-y-4 border-t border-slate-800 p-4 pt-3">
        {w.note && (
          <p className="rounded-lg border border-sky-500/20 bg-sky-500/[0.06] px-3 py-2 text-[11px] leading-relaxed text-sky-200/90">
            {w.note}
          </p>
        )}
        {w.findings.length > 0 && (
          <div>
            <div className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-slate-500">
              What we found
            </div>
            <ul className="space-y-1">
              {w.findings.map((f) => (
                <li key={f.rule_id} className="flex items-start gap-2 text-xs text-slate-300">
                  <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-signal-500" />
                  <span>
                    <span className="font-mono-num text-slate-500">{f.rule_id}</span> · {f.title}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}

        <div>
          <div className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-slate-500">
            To complete this workstream
          </div>
          <ul className="space-y-1">
            {w.checklist.map((c) => (
              <li key={c} className="flex items-start gap-2 text-xs text-slate-400">
                <span className="mt-1 text-[#4cc0b4]">□</span>
                {c}
              </li>
            ))}
          </ul>
        </div>

        {w.interview_targets && w.interview_targets.length > 0 && (
          <div>
            <div className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-slate-500">
              Reference-call targets
            </div>
            <div className="space-y-2">
              {w.interview_targets.map((t) => (
                <div key={t.name} className="rounded-lg border border-slate-800 bg-slate-950/40 p-2.5">
                  <div className="text-xs font-semibold text-slate-200">
                    {t.name}{' '}
                    <span className="font-mono-num font-normal text-slate-500">
                      {formatMoney(t.revenue)}
                      {t.share_pct ? ` · ${formatPct(t.share_pct)} of revenue` : ''}
                    </span>
                  </div>
                  <ul className="mt-1 space-y-0.5">
                    {t.script.map((q) => (
                      <li key={q} className="text-[11px] italic text-slate-400">
                        “{q}”
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </details>
  )
}

export default function WorkstreamsPanel({ workstreams }: { workstreams: Workstream[] }) {
  return (
    <div>
      <p className="mb-4 text-sm text-slate-400">
        Diligence is more than the numbers. Here is the whole engagement — what DealProofing has
        automated from the documents, and the checklists, data requests, and questions for the
        parts that are human-led.
      </p>
      <div className="grid gap-3 md:grid-cols-2">
        {workstreams.map((w) => (
          <WorkstreamCard key={w.key} w={w} />
        ))}
      </div>
    </div>
  )
}
