import type { ReactNode } from 'react'
import { NavLink } from 'react-router-dom'

interface NavItem {
  label: string
  to?: string
  locked?: boolean
}

const NAV_ITEMS: NavItem[] = [
  { label: 'Deals', to: '/deals' },
  { label: 'Reports', to: '/report' },
  { label: 'Benchmarks', locked: true },
  { label: 'Settings', locked: true },
  { label: 'Help', locked: true },
]

function LogoMark() {
  return (
    <div className="flex items-center gap-2 px-4 py-5">
      <svg width="20" height="20" viewBox="0 0 32 32" className="shrink-0">
        <rect width="32" height="32" rx="4" fill="#020617" />
        <path d="M16 6 L26 24 L6 24 Z" fill="none" stroke="#e5484d" strokeWidth="2" />
        <circle cx="16" cy="19" r="1.4" fill="#e5484d" />
      </svg>
      <span className="text-sm font-semibold tracking-wide text-slate-100">DealProof</span>
    </div>
  )
}

function SideNav() {
  return (
    <aside className="hidden w-56 shrink-0 flex-col border-r border-slate-800 bg-slate-900/60 md:flex">
      <LogoMark />
      <nav className="flex-1 space-y-0.5 px-2">
        {NAV_ITEMS.map((item) =>
          item.locked || !item.to ? (
            <div
              key={item.label}
              className="flex cursor-not-allowed items-center justify-between rounded px-3 py-2 text-sm text-slate-600"
              title="Coming soon"
            >
              <span>{item.label}</span>
              <LockIcon />
            </div>
          ) : (
            <NavLink
              key={item.label}
              to={item.to}
              className={({ isActive }) =>
                `block rounded px-3 py-2 text-sm transition ${
                  isActive
                    ? 'bg-slate-800 text-slate-100'
                    : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                }`
              }
            >
              {item.label}
            </NavLink>
          ),
        )}
      </nav>
      <div className="border-t border-slate-800 px-4 py-4 text-[11px] text-slate-600">
        <p>Institutional-grade diligence</p>
        <p className="mt-0.5">v0.1 &middot; demo workspace</p>
      </div>
    </aside>
  )
}

function LockIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" className="text-slate-700">
      <rect x="5" y="11" width="14" height="9" rx="1.5" stroke="currentColor" strokeWidth="1.6" />
      <path d="M8 11V8a4 4 0 0 1 8 0v3" stroke="currentColor" strokeWidth="1.6" />
    </svg>
  )
}

function TopBar({ title }: { title?: string }) {
  return (
    <header className="flex h-14 items-center justify-between border-b border-slate-800 bg-slate-950/80 px-6">
      <div className="flex items-center gap-2 md:hidden">
        <LogoMark />
      </div>
      <h1 className="text-sm font-medium text-slate-300">{title}</h1>
      <div className="flex items-center gap-3">
        <div className="h-7 w-7 rounded-full bg-slate-800 text-center text-xs leading-7 text-slate-400">
          TB
        </div>
      </div>
    </header>
  )
}

export default function AppShell({ children, title }: { children: ReactNode; title?: string }) {
  return (
    <div className="flex min-h-screen bg-slate-950">
      <SideNav />
      <div className="flex min-h-screen flex-1 flex-col">
        <TopBar title={title} />
        <main className="flex-1">{children}</main>
      </div>
    </div>
  )
}
