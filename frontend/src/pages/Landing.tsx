import { useState } from 'react'
import { Link } from 'react-router-dom'

const DEMO_SRC = `${import.meta.env.BASE_URL}dealproofing-demo.mp4`

function PlayIcon({ className = '' }: { className?: string }) {
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" className={className} aria-hidden="true">
      <path d="M4 3 L13 8 L4 13 Z" fill="currentColor" />
    </svg>
  )
}

function DemoModal({ onClose }: { onClose: () => void }) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/85 p-4 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      onClick={onClose}
    >
      <div className="w-full max-w-4xl" onClick={(e) => e.stopPropagation()}>
        <div className="mb-3 flex items-center justify-between">
          <span className="text-sm font-semibold text-slate-200">DealProofing — 2-minute demo</span>
          <button
            onClick={onClose}
            className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs text-slate-300 transition hover:border-slate-500 hover:text-slate-100"
          >
            Close
          </button>
        </div>
        <video
          src={DEMO_SRC}
          controls
          autoPlay
          playsInline
          className="w-full rounded-xl border border-slate-800 bg-black shadow-2xl"
        />
      </div>
    </div>
  )
}

const STEPS = [
  {
    n: '01',
    title: 'Upload the seller’s paperwork',
    body: 'Drop in the tax returns, profit statements, bank records, lease, and contracts the seller gave you. The messy pile is fine — we sort it out.',
  },
  {
    n: '02',
    title: 'We cross-check the numbers',
    body: 'The same figures get compared across the tax return, the profit report, and the money that actually hit the bank. Where they disagree is where the risk hides.',
  },
  {
    n: '03',
    title: 'You get a plain-English report',
    body: 'A clear list of what looks risky — ranked by how serious — each backed by the exact source page and the question to ask the seller.',
  },
]

const VALUE = [
  {
    title: 'Warning signs, ranked',
    body: 'The specific risks worth investigating, sorted by how serious. Red first, so you know where to look.',
    icon: (
      <path d="M16 4.5 L26 8 V15.2 C26 21.8 21.7 26.4 16 27.8 C10.3 26.4 6 21.8 6 15.2 V8 Z M11.4 15.8 L14.7 19.1 L20.6 12.4"
        fill="none" strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
    ),
  },
  {
    title: 'Proof you can check',
    body: 'Every number links to the exact document page it came from. No black box — you can verify it yourself.',
    icon: (
      <>
        <circle cx="14" cy="14" r="8" fill="none" strokeWidth="2" />
        <path d="M20 20 L27 27" fill="none" strokeWidth="2" strokeLinecap="round" />
      </>
    ),
  },
  {
    title: 'The right questions to ask',
    body: 'A ready-made list of exactly what to put to the seller about each issue — so the hard conversation is easy.',
    icon: (
      <path d="M6 8 H26 V21 H14 L8 26 V21 H6 Z" fill="none" strokeWidth="2" strokeLinejoin="round" />
    ),
  },
]

const PLANS = [
  {
    name: 'Snapshot',
    price: '$499',
    cadence: 'one-time',
    blurb: 'A fast gut-check before you spend real diligence budget.',
    features: ['Triangle of Truth reconciliation', 'Top red flags only', 'Automated report'],
  },
  {
    name: 'Full Diligence Report',
    price: '$2,950',
    cadence: 'one-time',
    blurb: 'The complete red-flag ledger with human review and evidence.',
    features: [
      'Full red-flag ledger with evidence',
      'Human-reviewed narrative',
      'Seller question pack',
      'Benchmark comparison',
    ],
    highlight: true,
  },
  {
    name: 'Deal Desk',
    price: '$1,500/mo',
    cadence: '+ $1,950 per deal',
    blurb: 'For buyers running several deals at once.',
    features: ['Unlimited deal dashboard', 'Priority 48h turnaround', 'Dedicated analyst contact'],
  },
  {
    name: 'Broker White-Label',
    price: '$6k/yr',
    cadence: '+ $1,750 per deal',
    blurb: 'Offer serious diligence under your own brand.',
    features: ['White-labeled reports', 'Broker portal access', 'Volume pricing'],
  },
]

const FAQS = [
  {
    q: 'What is DealProofing?',
    a: 'A warning-sign scanner for business purchases. We check the numbers a seller gives you against each other and surface the specific things worth investigating — before you spend money on lawyers and accountants.',
  },
  {
    q: 'What is DealProofing NOT?',
    a: 'We are not a CPA firm. We do not perform a Quality of Earnings engagement. Nothing we produce is financial, legal, or valuation advice. Findings simply point you to areas for further professional review.',
  },
  {
    q: 'Do I need to be a finance person to use it?',
    a: 'No. The whole point is plain English. Every finding says what it means, why it matters, and what to ask — no jargon required.',
  },
  {
    q: 'Do you give a single score or tell me whether to buy?',
    a: 'No — on purpose. DealProofing produces no single score and no go/no-go call. Only findings, the evidence behind them, and questions for the seller. The decision stays yours.',
  },
]

const TEAL = '#4cc0b4'

function Logo() {
  return (
    <div className="flex items-center gap-2">
      <svg width="26" height="26" viewBox="0 0 32 32" className="shrink-0" aria-hidden="true">
        <rect width="32" height="32" rx="7" fill="#0b1220" />
        <path
          d="M16 4.5 L26 8 V15.2 C26 21.8 21.7 26.4 16 27.8 C10.3 26.4 6 21.8 6 15.2 V8 Z"
          fill="none" stroke={TEAL} strokeWidth="2" strokeLinejoin="round"
        />
        <path
          d="M11.4 15.8 L14.7 19.1 L20.6 12.4"
          fill="none" stroke={TEAL} strokeWidth="2.3" strokeLinecap="round" strokeLinejoin="round"
        />
      </svg>
      <span className="text-base font-semibold tracking-wide">DealProofing</span>
    </div>
  )
}

/** A miniature of the real report — shows a visitor exactly what they'll get. */
function ReportPreview() {
  const tiles = [
    { n: 4, label: 'Critical', color: '#ef5b57', dim: false },
    { n: 2, label: 'High', color: '#e2953f', dim: false },
    { n: 0, label: 'Medium', color: '#64748b', dim: true },
    { n: 1, label: 'Info', color: '#6aa2f2', dim: false },
  ]
  // 2024 revenue from three sources (tax / P&L / bank), scaled to bar heights.
  const bars = [
    { label: 'Tax', h: 78, c: '#3987e5' },
    { label: 'P&L', h: 80, c: '#199e70' },
    { label: 'Bank', h: 62, c: '#9085e9' },
  ]
  return (
    <div className="relative">
      <div className="pointer-events-none absolute -inset-6 rounded-[28px] bg-[#4cc0b4]/10 blur-2xl" />
      <div className="relative rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-2xl backdrop-blur">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div>
            <div className="text-sm font-semibold text-slate-100">Summit Air Mechanical</div>
            <div className="font-mono-num text-xs text-slate-500">HVAC · Asking $1,560,000</div>
          </div>
          <span className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-emerald-400">
            Report ready
          </span>
        </div>

        <div className="mt-4 grid grid-cols-4 gap-2">
          {tiles.map((t) => (
            <div
              key={t.label}
              className={`rounded-lg border border-slate-800 bg-slate-950/60 px-2 py-2 text-center ${t.dim ? 'opacity-50' : ''}`}
            >
              <div className="font-mono-num text-xl font-bold" style={{ color: t.dim ? '#64748b' : t.color }}>
                {t.n}
              </div>
              <div className="text-[9px] uppercase tracking-wide text-slate-500">{t.label}</div>
            </div>
          ))}
        </div>

        <div className="mt-4 rounded-lg border border-slate-800 bg-slate-950/40 p-3">
          <div className="mb-2 text-[10px] uppercase tracking-wider text-slate-500">
            2024 revenue · three sources
          </div>
          <div className="flex items-end gap-4 px-1" style={{ height: 84 }}>
            {bars.map((b) => (
              <div key={b.label} className="flex flex-1 flex-col items-center gap-1">
                <div className="flex w-full items-end justify-center" style={{ height: 64 }}>
                  <div
                    className="w-6 rounded-t"
                    style={{ height: `${b.h}%`, background: b.c }}
                    title={b.label}
                  />
                </div>
                <div className="font-mono-num text-[10px] text-slate-500">{b.label}</div>
              </div>
            ))}
          </div>
          <div className="mt-1 text-[11px] text-slate-400">
            Bank deposits were only <span className="font-mono-num font-semibold text-[#ef5b57]">78%</span> of
            reported revenue.
          </div>
        </div>

        <div className="mt-3 flex items-start gap-2 rounded-lg border-l-2 border-[#ef5b57] bg-slate-950/50 px-3 py-2">
          <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-[#ef5b57]" />
          <div>
            <div className="text-xs font-semibold text-slate-100">Where did the missing cash go?</div>
            <div className="text-[11px] text-slate-500">
              Over $500,000 of claimed sales never reached the bank.
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function Landing() {
  const [demoOpen, setDemoOpen] = useState(false)
  return (
    <div className="relative min-h-screen overflow-hidden bg-slate-950 text-slate-100">
      {demoOpen && <DemoModal onClose={() => setDemoOpen(false)} />}
      {/* warm ambient glows so the page never feels blank */}
      <div className="pointer-events-none absolute -left-40 -top-40 h-[32rem] w-[32rem] rounded-full bg-[#4cc0b4]/10 blur-[120px]" />
      <div className="pointer-events-none absolute right-[-12rem] top-40 h-[34rem] w-[34rem] rounded-full bg-blue-500/10 blur-[130px]" />

      <header className="relative z-10 mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <Logo />
        <div className="flex items-center gap-2 sm:gap-3">
          <button
            onClick={() => setDemoOpen(true)}
            className="inline-flex items-center gap-2 rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-200 transition hover:border-[#4cc0b4]/60 hover:bg-slate-800/40"
          >
            <PlayIcon className="text-[#4cc0b4]" />
            Watch demo
          </button>
          <Link
            to="/report"
            className="hidden rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-200 transition hover:border-slate-500 hover:bg-slate-800/40 md:inline-block"
          >
            See a sample report
          </Link>
          <Link
            to="/login"
            className="rounded-lg bg-[#4cc0b4] px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-[#3aa99d]"
          >
            Sign in
          </Link>
        </div>
      </header>

      {/* Hero */}
      <section className="relative z-10 mx-auto max-w-6xl px-6 pb-20 pt-10 lg:pt-16">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          <div>
            <p className="mb-5 inline-flex items-center gap-2 rounded-full border border-slate-800 bg-slate-900/60 px-3 py-1 text-xs text-slate-300">
              <span className="h-1.5 w-1.5 rounded-full bg-[#4cc0b4]" />
              For anyone buying a small business
            </p>
            <h1 className="text-4xl font-bold leading-[1.1] tracking-tight text-slate-50 sm:text-5xl">
              Know what you’re
              <br />
              buying —{' '}
              <span className="bg-gradient-to-r from-[#5fd0c4] to-[#7cc0ff] bg-clip-text text-transparent">
                before you pay.
              </span>
            </h1>
            <p className="mt-5 max-w-xl text-lg leading-relaxed text-slate-300">
              Upload the seller’s financials. In minutes, DealProofing shows you the warning signs — and
              the exact questions to ask — so you spend your money with your eyes open.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Link
                to="/report"
                className="rounded-lg bg-[#4cc0b4] px-6 py-3 text-center text-sm font-semibold text-slate-950 shadow-lg shadow-[#4cc0b4]/20 transition hover:bg-[#3aa99d]"
              >
                See a real example →
              </Link>
              <Link
                to="/login"
                className="rounded-lg border border-slate-700 px-6 py-3 text-center text-sm font-semibold text-slate-200 transition hover:border-slate-500 hover:bg-slate-800/40"
              >
                Try it with your deal
              </Link>
            </div>
            <button
              onClick={() => setDemoOpen(true)}
              className="mt-4 inline-flex items-center gap-2 text-sm text-slate-300 transition hover:text-[#4cc0b4]"
            >
              <span className="flex h-7 w-7 items-center justify-center rounded-full border border-[#4cc0b4]/40 bg-[#4cc0b4]/10">
                <PlayIcon className="text-[#4cc0b4]" />
              </span>
              Watch the 2-minute demo
            </button>
            <div className="mt-6 flex flex-wrap gap-x-5 gap-y-2 text-xs text-slate-500">
              <span>✓ Plain English</span>
              <span>✓ Every number linked to its source</span>
              <span>✓ No score, no sales pitch</span>
            </div>
          </div>

          <ReportPreview />
        </div>
      </section>

      {/* What you get */}
      <section className="relative z-10 border-t border-slate-900 bg-slate-900/30 py-20">
        <div className="mx-auto max-w-6xl px-6">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-2xl font-bold text-slate-100 sm:text-3xl">
              A $50,000 check-up, as a first pass
            </h2>
            <p className="mt-3 text-slate-400">
              You don’t need to be a finance person. Here’s what you walk away with.
            </p>
          </div>
          <div className="mt-12 grid gap-6 md:grid-cols-3">
            {VALUE.map((v) => (
              <div
                key={v.title}
                className="rounded-xl border border-slate-800 bg-slate-950/60 p-6 transition hover:border-[#4cc0b4]/40 hover:bg-slate-900/50"
              >
                <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-[#4cc0b4]/10">
                  <svg width="24" height="24" viewBox="0 0 32 32" stroke="#4cc0b4">
                    {v.icon}
                  </svg>
                </div>
                <h3 className="mt-4 text-lg font-semibold text-slate-100">{v.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-400">{v.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="relative z-10 border-t border-slate-900 py-20">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="text-center text-sm font-semibold uppercase tracking-widest text-[#4cc0b4]">
            How it works
          </h2>
          <p className="mt-2 text-center text-2xl font-bold text-slate-100">Three steps, about five minutes</p>
          <div className="mt-12 grid gap-8 md:grid-cols-3">
            {STEPS.map((step) => (
              <div key={step.n} className="relative rounded-xl border border-slate-800 bg-slate-900/40 p-6">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#4cc0b4]/10 font-mono-num text-sm font-bold text-[#4cc0b4]">
                  {step.n}
                </div>
                <h3 className="mt-4 text-lg font-semibold text-slate-100">{step.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-400">{step.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="relative z-10 border-t border-slate-900 bg-slate-900/30 py-20">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="text-center text-sm font-semibold uppercase tracking-widest text-[#4cc0b4]">
            Simple, flat pricing
          </h2>
          <p className="mt-2 text-center text-2xl font-bold text-slate-100">Pay per deal. No subscriptions to start.</p>
          <div className="mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
            {PLANS.map((plan) => (
              <div
                key={plan.name}
                className={`flex flex-col rounded-xl border p-6 ${
                  plan.highlight
                    ? 'border-[#4cc0b4]/50 bg-[#4cc0b4]/[0.06] shadow-lg shadow-[#4cc0b4]/10'
                    : 'border-slate-800 bg-slate-950/50'
                }`}
              >
                {plan.highlight && (
                  <span className="mb-3 self-start rounded-full bg-[#4cc0b4] px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-slate-950">
                    Most popular
                  </span>
                )}
                <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-300">{plan.name}</h3>
                <div className="mt-3 font-mono-num text-2xl font-semibold text-slate-50">{plan.price}</div>
                <div className="font-mono-num text-xs text-slate-500">{plan.cadence}</div>
                <p className="mt-3 text-xs text-slate-400">{plan.blurb}</p>
                <ul className="mt-4 flex-1 space-y-2 text-xs text-slate-400">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-start gap-2">
                      <span className="mt-0.5 text-[#4cc0b4]">✓</span>
                      {f}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="relative z-10 border-t border-slate-900 py-20">
        <div className="mx-auto max-w-4xl px-6">
          <h2 className="text-center text-2xl font-bold text-slate-100">Questions, answered plainly</h2>
          <div className="mt-10 space-y-4">
            {FAQS.map((faq) => (
              <div key={faq.q} className="rounded-xl border border-slate-800 bg-slate-900/40 p-5">
                <h3 className="text-sm font-semibold text-slate-100">{faq.q}</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-400">{faq.a}</p>
              </div>
            ))}
          </div>

          <div className="mt-10 rounded-xl border border-slate-800 bg-slate-950/50 p-5">
            <p className="text-xs leading-relaxed text-slate-500">
              DealProofing is an automated document-analysis and red-flag identification tool. It does not
              provide accounting, legal, tax, investment, or valuation advice; is not a CPA firm; and does
              not perform a Quality of Earnings engagement. Findings identify areas for further
              professional review.
            </p>
          </div>
        </div>
      </section>

      {/* Closing CTA */}
      <section className="relative z-10 border-t border-slate-900 py-20">
        <div className="mx-auto max-w-3xl px-6 text-center">
          <h2 className="text-3xl font-bold text-slate-50">See it on a real deal in 30 seconds</h2>
          <p className="mt-3 text-slate-400">
            No sign-up needed for the sample report — take a look and decide for yourself.
          </p>
          <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
            <Link
              to="/report"
              className="rounded-lg bg-[#4cc0b4] px-7 py-3 text-sm font-semibold text-slate-950 transition hover:bg-[#3aa99d]"
            >
              See a sample report →
            </Link>
            <Link
              to="/login"
              className="rounded-lg border border-slate-700 px-7 py-3 text-sm font-semibold text-slate-200 transition hover:border-slate-500 hover:bg-slate-800/40"
            >
              Launch the app
            </Link>
          </div>
        </div>
      </section>

      <footer className="relative z-10 border-t border-slate-900 py-10">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 text-xs text-slate-600 sm:flex-row">
          <span>&copy; {new Date().getFullYear()} DealProofing.</span>
          <Link to="/report" className="text-slate-400 transition hover:text-[#4cc0b4]">
            See a sample report →
          </Link>
        </div>
      </footer>
    </div>
  )
}
