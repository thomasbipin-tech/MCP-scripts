import { useState } from 'react'
import type { ExpertPacket, ExpertPackets } from '../types/report'

function packetToText(p: ExpertPacket): string {
  const lines = [`${p.title}`, `For: ${p.audience}`, '', p.purpose, '']
  for (const s of p.sections) {
    lines.push(s.heading.toUpperCase())
    for (const i of s.items) lines.push(`  • ${i}`)
    lines.push('')
  }
  if (p.questions.length) {
    lines.push('QUESTIONS')
    for (const q of p.questions) lines.push(`  • ${q}`)
  }
  return lines.join('\n')
}

function PacketCard({ packet }: { packet: ExpertPacket }) {
  const [copied, setCopied] = useState(false)

  async function copy() {
    try {
      await navigator.clipboard.writeText(packetToText(packet))
      setCopied(true)
      setTimeout(() => setCopied(false), 1800)
    } catch {
      // Clipboard unavailable (e.g. insecure context) — no-op, the text is on screen.
    }
  }

  return (
    <div className="flex h-full flex-col rounded-xl border border-slate-800 bg-slate-900/40 p-4">
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <h3 className="text-sm font-semibold text-slate-100">{packet.title}</h3>
          <p className="text-[11px] uppercase tracking-wide text-[#4cc0b4]">{packet.audience}</p>
        </div>
        <button
          onClick={copy}
          className="shrink-0 rounded border border-slate-700 px-2 py-1 text-[11px] font-medium text-slate-300 transition hover:border-slate-500"
        >
          {copied ? 'Copied ✓' : 'Copy'}
        </button>
      </div>
      <p className="mt-2 text-xs leading-relaxed text-slate-400">{packet.purpose}</p>

      <div className="mt-3 space-y-3 border-t border-slate-800 pt-3">
        {packet.sections.map((s) => (
          <div key={s.heading}>
            <div className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-slate-500">
              {s.heading}
            </div>
            <ul className="space-y-1">
              {s.items.map((i, idx) => (
                <li key={idx} className="flex items-start gap-2 text-xs text-slate-300">
                  <span className="mt-1 h-1 w-1 shrink-0 rounded-full bg-slate-600" />
                  <span>{i}</span>
                </li>
              ))}
            </ul>
          </div>
        ))}

        {packet.questions.length > 0 && (
          <div>
            <div className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-slate-500">
              Questions
            </div>
            <ul className="space-y-1">
              {packet.questions.map((q, idx) => (
                <li key={idx} className="text-[11px] italic text-slate-400">
                  “{q}”
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}

export default function ExpertPacketsPanel({ packets }: { packets: ExpertPackets }) {
  return (
    <div>
      <p className="mb-4 text-sm text-slate-400">
        Diligence ends with humans making the call. These packets hand your CPA, attorney and lender a
        focused, evidence-cited brief so they start at the finish line — DealProofing surfaces, your
        experts decide.
      </p>
      <div className="grid gap-3 md:grid-cols-3">
        <PacketCard packet={packets.qofe} />
        <PacketCard packet={packets.attorney} />
        <PacketCard packet={packets.lender} />
      </div>
    </div>
  )
}
