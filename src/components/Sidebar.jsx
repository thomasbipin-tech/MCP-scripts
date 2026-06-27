import { SlidersHorizontal, PenLine, Layers } from 'lucide-react'

// Left navigation rail. Each entry switches the active page; the app stays
// mounted so song state is preserved across page switches.
const PAGES = [
  { id: 'studio', label: 'Studio', icon: SlidersHorizontal },
  { id: 'lyrics', label: 'Lyrics AI', icon: PenLine },
  { id: 'super', label: 'Super Generate', icon: Layers },
]

export default function Sidebar({ page, onNavigate, open }) {
  return (
    <nav className={`sidebar glass${open ? ' open' : ''}`} aria-label="Pages" aria-hidden={!open}>
      {PAGES.map(({ id, label, icon: Icon }) => (
        <button
          key={id}
          type="button"
          className={`nav-item${page === id ? ' active' : ''}`}
          aria-current={page === id ? 'page' : undefined}
          onClick={() => onNavigate(id)}
        >
          <Icon size={17} />
          <span>{label}</span>
        </button>
      ))}

      <div
        className="autosave-tag mono"
        style={{
          marginTop: 'auto',
          fontSize: 9,
          letterSpacing: '0.1em',
          textTransform: 'uppercase',
          color: 'var(--neon-green)',
          display: 'flex',
          alignItems: 'center',
          gap: 6,
        }}
      >
        <span style={{ fontSize: 8 }}>●</span> Auto-saved
      </div>
    </nav>
  )
}
