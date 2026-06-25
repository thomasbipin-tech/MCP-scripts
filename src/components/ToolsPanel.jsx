import { AudioLines } from 'lucide-react'

// A simple "Tools" section in the left column. For now it holds a single
// labelled entry, "Suno".
export default function ToolsPanel() {
  return (
    <section className="glass" style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 12 }}>
      <span className="label">Tools</span>

      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          padding: '10px 12px',
          borderRadius: 10,
          background: 'rgba(177,76,255,0.08)',
          border: '1px solid rgba(177,76,255,0.25)',
          color: 'var(--neon-purple)',
        }}
      >
        <AudioLines size={16} />
        <span style={{ fontSize: 14, fontWeight: 600, letterSpacing: '0.02em' }}>Suno</span>
      </div>
    </section>
  )
}
