import type { ReactNode } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

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
      <svg width="20" height="20" viewBox="0 0 32 32" className="shrink-0" aria-hidden="true">
        <rect width="32" height="32" rx="7" fill="#0b1220" />
        <path
          d="M16 4.5 L26 8 V15.2 C26 21.8 21.7 26.4 16 27.8 C10.3 26.4 6 21.8 6 15.2 V8 Z"
          fill="none" stroke="#4cc0b4" strokeWidth="2" strokeLinejoin="round"
        />
        <path
          d="M11.4 15.8 L14.7 19.1 L20.6 12.4"
          fill="none" stroke="#4cc0b4" strokeWidth="2.3" strokeLinecap="round" strokeLinejoin="round"
        />
      </svg>
      <span className="text-sm font-semibold tracking-wide text-slate-100">DealProofing</span>
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
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <header className="flex h-14 items-center justify-between border-b border-slate-800 bg-slate-950/80 px-4 sm:px-6">
      <div className="flex items-center gap-2 md:hidden">
        <LogoMark />
      </div>
      <h1 className="hidden truncate text-sm font-medium text-slate-300 sm:block">{title}</h1>
      <div className="flex min-w-0 items-center gap-2 sm:gap-3">
        {user ? (
          <>
            <span className="hidden max-w-[180px] truncate text-xs text-slate-400 md:inline">
              {user.email}
            </span>
            <div className="h-7 w-7 shrink-0 rounded-full bg-slate-800 text-center text-xs font-semibold leading-7 text-slate-400">
              {user.email.slice(0, 2).toUpperCase()}
            </div>
            <button
              onClick={handleLogout}
              className="shrink-0 rounded border border-slate-700 px-2.5 py-1.5 text-xs text-slate-300 transition hover:border-slate-500 hover:text-slate-100"
            >
              Logout
            </button>
          </>
        ) : (
          <Link
            to="/login"
            className="shrink-0 rounded border border-slate-700 px-3 py-1.5 text-xs text-slate-200 transition hover:border-slate-500"
          >
            Sign in
          </Link>
        )}
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
