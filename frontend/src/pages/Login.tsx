import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { apiPost } from '../lib/api'
import { useAuth } from '../context/AuthContext'
import type { MagicRequestResponse, TokenResponse } from '../types/api'

type Status = 'idle' | 'sending' | 'sent' | 'error'

export default function Login() {
  const [email, setEmail] = useState('')
  const [status, setStatus] = useState<Status>('idle')
  const [error, setError] = useState<string | null>(null)
  const [busyDemo, setBusyDemo] = useState<'admin' | 'buyer' | null>(null)
  const { login } = useAuth()
  const navigate = useNavigate()

  async function runMagicFlow(targetEmail: string) {
    setError(null)
    setStatus('sending')
    try {
      const req = await apiPost<MagicRequestResponse>('/auth/request', { email: targetEmail })
      if (req.magic_token) {
        const tok = await apiPost<TokenResponse>('/auth/verify', { token: req.magic_token })
        await login(tok.access_token)
        navigate('/deals')
        return
      }
      setStatus('sent')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Something went wrong. Please try again.')
      setStatus('error')
    }
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!email.trim()) return
    await runMagicFlow(email.trim())
  }

  async function handleDemo(role: 'admin' | 'buyer') {
    setBusyDemo(role)
    const demoEmail = role === 'admin' ? 'admin@dealproof.test' : 'buyer@dealproof.test'
    setEmail(demoEmail)
    await runMagicFlow(demoEmail)
    setBusyDemo(null)
  }

  const sending = status === 'sending'

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 px-4 py-10">
      <div className="w-full max-w-sm rounded border border-slate-800 bg-slate-900/40 p-6 sm:p-8">
        <div className="mb-6 flex items-center gap-2">
          <svg width="22" height="22" viewBox="0 0 32 32" className="shrink-0">
            <rect width="32" height="32" rx="4" fill="#020617" />
            <path d="M16 6 L26 24 L6 24 Z" fill="none" stroke="#e5484d" strokeWidth="2" />
            <circle cx="16" cy="19" r="1.4" fill="#e5484d" />
          </svg>
          <span className="text-base font-semibold tracking-wide text-slate-100">DealProof</span>
        </div>

        <h1 className="text-lg font-semibold text-slate-100">Sign in</h1>
        <p className="mt-1 text-sm text-slate-500">We'll email you a magic link. No password.</p>

        {status === 'sent' ? (
          <div className="mt-6 rounded border border-emerald-500/30 bg-emerald-500/10 p-4 text-sm text-emerald-300">
            Check your email for a sign-in link.
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="mt-6 space-y-3">
            <label className="block">
              <span className="mb-1.5 block text-xs font-medium uppercase tracking-wide text-slate-500">
                Email
              </span>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-slate-100 outline-none transition placeholder:text-slate-600 focus:border-slate-500"
              />
            </label>
            <button
              type="submit"
              disabled={sending}
              className="w-full rounded bg-signal-500 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-signal-600 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {sending ? 'Sending…' : 'Send magic link'}
            </button>
          </form>
        )}

        {error && <p className="mt-3 text-xs text-signal-400">{error}</p>}

        <div className="mt-6 border-t border-slate-800 pt-6">
          <p className="mb-3 text-xs uppercase tracking-wide text-slate-600">Demo shortcuts</p>
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <button
              onClick={() => handleDemo('admin')}
              disabled={busyDemo !== null || sending}
              className="rounded border border-slate-700 px-3 py-2.5 text-xs font-medium text-slate-200 transition hover:border-slate-500 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {busyDemo === 'admin' ? 'Signing in…' : 'Continue as admin (demo)'}
            </button>
            <button
              onClick={() => handleDemo('buyer')}
              disabled={busyDemo !== null || sending}
              className="rounded border border-slate-700 px-3 py-2.5 text-xs font-medium text-slate-200 transition hover:border-slate-500 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {busyDemo === 'buyer' ? 'Signing in…' : 'Continue as buyer (demo)'}
            </button>
          </div>
          <p className="mt-3 text-[11px] leading-relaxed text-slate-600">
            Sign in as admin to publish reports.
          </p>
        </div>

        <div className="mt-6 flex justify-between text-xs text-slate-500">
          <Link to="/" className="hover:text-slate-300">
            &larr; Back home
          </Link>
          <Link to="/report" className="hover:text-slate-300">
            View sample report
          </Link>
        </div>
      </div>
    </div>
  )
}
