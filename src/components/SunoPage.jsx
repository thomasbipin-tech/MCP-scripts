import { AudioLines } from 'lucide-react'

// Placeholder Suno page. Kept as a labelled page for now; ask the assistant to
// wire it up to real song generation when you're ready.
export default function SunoPage() {
  return (
    <section className="glass page-pane" style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 12 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, color: 'var(--neon-purple)' }}>
        <AudioLines size={20} />
        <span style={{ fontSize: 18, fontWeight: 700 }}>Suno</span>
      </div>
      <p style={{ color: 'var(--text-dim)', fontSize: 14, maxWidth: 460, lineHeight: 1.6 }}>
        Placeholder page. When you're ready, tell the assistant what Suno should do here —
        for example, generate a full song from a text prompt.
      </p>
    </section>
  )
}
