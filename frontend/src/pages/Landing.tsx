import { Link } from 'react-router-dom'

const STEPS = [
  {
    n: '01',
    title: 'Upload the data room',
    body: 'Drop in tax returns, P&Ls, bank statements, leases, and contracts. We accept the messy pile a seller actually hands you.',
  },
  {
    n: '02',
    title: 'Triangle of Truth reconciliation + red-flag scan',
    body: 'We cross-reference tax filings, P&L, and bank deposits, then run a rules engine tuned to small-business acquisition risk.',
  },
  {
    n: '03',
    title: 'Human-reviewed report in 48h',
    body: 'A analyst reviews every automated finding before it reaches you, with evidence linked to the exact page it came from.',
  },
]

const PLANS = [
  {
    name: 'Snapshot',
    price: '$499',
    cadence: 'one-time',
    blurb: 'A fast gut-check before you spend real diligence budget.',
    features: ['Triangle of Truth reconciliation', 'Top red flags only', 'Automated report, no analyst review'],
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
    blurb: 'For buyers running multiple deals concurrently.',
    features: ['Unlimited deal dashboard', 'Priority 48h turnaround', 'Dedicated analyst contact'],
  },
  {
    name: 'Broker White-Label',
    price: '$6k/yr',
    cadence: '+ $1,750 per deal',
    blurb: 'Offer institutional-grade diligence under your own brand.',
    features: ['White-labeled reports', 'Broker portal access', 'Volume pricing on deal fees'],
  },
]

const FAQS = [
  {
    q: 'What is DealProof?',
    a: 'A red-flag scanner and diligence accelerant. We reconcile the numbers a seller gives you against each other and surface the specific issues worth investigating before you spend money on lawyers and accountants.',
  },
  {
    q: 'What is DealProof NOT?',
    a: 'We are not a CPA firm. We do not perform a Quality of Earnings engagement. Nothing we produce is financial, legal, or valuation advice. Findings identify areas for further professional review.',
  },
  {
    q: 'How fast is turnaround?',
    a: 'Full Diligence Reports are delivered within 48 hours of a complete data room upload.',
  },
  {
    q: 'Do you give a single risk score or a recommendation?',
    a: 'No. DealProof intentionally produces no single score and no go/no-go recommendation — only findings, evidence, and questions for the seller.',
  },
]

export default function Landing() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <div className="flex items-center gap-2">
          <svg width="22" height="22" viewBox="0 0 32 32" className="shrink-0">
            <rect width="32" height="32" rx="4" fill="#020617" />
            <path d="M16 6 L26 24 L6 24 Z" fill="none" stroke="#e5484d" strokeWidth="2" />
            <circle cx="16" cy="19" r="1.4" fill="#e5484d" />
          </svg>
          <span className="text-base font-semibold tracking-wide">DealProof</span>
        </div>
        <div className="flex items-center gap-2 sm:gap-3">
          <Link
            to="/report"
            className="hidden rounded border border-slate-700 px-4 py-2 text-sm text-slate-200 transition hover:border-slate-500 sm:inline-block"
          >
            View a sample report
          </Link>
          <Link
            to="/login"
            className="rounded bg-signal-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-signal-600"
          >
            Sign in
          </Link>
        </div>
      </header>

      {/* Hero */}
      <section className="mx-auto max-w-5xl px-6 pb-24 pt-16 text-center">
        <p className="mb-4 inline-block rounded-full border border-slate-800 px-3 py-1 text-xs uppercase tracking-widest text-slate-400">
          Small-business acquisition diligence
        </p>
        <h1 className="text-5xl font-bold leading-tight tracking-tight text-slate-50 sm:text-6xl">
          Know before you buy.
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-400">
          Institutional-grade red-flag analysis on any small business acquisition. 48 hours. Flat fee.
        </p>
        <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <Link
            to="/report"
            className="rounded bg-signal-500 px-6 py-3 text-sm font-semibold text-white transition hover:bg-signal-600"
          >
            View a sample report
          </Link>
          <Link
            to="/login"
            className="rounded border border-slate-700 px-6 py-3 text-sm font-semibold text-slate-200 transition hover:border-slate-500"
          >
            Launch app
          </Link>
        </div>
      </section>

      {/* How it works */}
      <section className="border-t border-slate-900 bg-slate-900/30 py-20">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="text-center text-sm font-semibold uppercase tracking-widest text-slate-500">
            How it works
          </h2>
          <div className="mt-10 grid gap-8 md:grid-cols-3">
            {STEPS.map((step) => (
              <div key={step.n} className="rounded border border-slate-800 bg-slate-950/60 p-6">
                <div className="font-mono-num text-2xl text-signal-500">{step.n}</div>
                <h3 className="mt-3 text-lg font-semibold text-slate-100">{step.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-400">{step.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="border-t border-slate-900 py-20">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="text-center text-sm font-semibold uppercase tracking-widest text-slate-500">
            Pricing
          </h2>
          <div className="mt-10 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
            {PLANS.map((plan) => (
              <div
                key={plan.name}
                className={`flex flex-col rounded border p-6 ${
                  plan.highlight
                    ? 'border-signal-500/40 bg-signal-500/[0.04]'
                    : 'border-slate-800 bg-slate-900/40'
                }`}
              >
                <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-300">
                  {plan.name}
                </h3>
                <div className="mt-3 font-mono-num text-2xl font-semibold text-slate-50">
                  {plan.price}
                </div>
                <div className="font-mono-num text-xs text-slate-500">{plan.cadence}</div>
                <p className="mt-3 text-xs text-slate-400">{plan.blurb}</p>
                <ul className="mt-4 flex-1 space-y-2 text-xs text-slate-400">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-start gap-2">
                      <span className="mt-1 h-1 w-1 shrink-0 rounded-full bg-slate-600" />
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
      <section className="border-t border-slate-900 bg-slate-900/30 py-20">
        <div className="mx-auto max-w-4xl px-6">
          <h2 className="text-center text-sm font-semibold uppercase tracking-widest text-slate-500">
            FAQ
          </h2>
          <div className="mt-10 space-y-4">
            {FAQS.map((faq) => (
              <div key={faq.q} className="rounded border border-slate-800 bg-slate-950/60 p-5">
                <h3 className="text-sm font-semibold text-slate-100">{faq.q}</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-400">{faq.a}</p>
              </div>
            ))}
          </div>

          <div className="mt-8 rounded border border-signal-500/30 bg-signal-500/[0.04] p-5">
            <p className="text-xs leading-relaxed text-slate-400">
              DealProof is an automated document-analysis and red-flag identification tool. It does not
              provide accounting, legal, tax, investment, or valuation advice; is not a CPA firm; and does
              not perform a Quality of Earnings engagement. Findings identify areas for further
              professional review.
            </p>
          </div>
        </div>
      </section>

      <footer className="border-t border-slate-900 py-10">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 text-xs text-slate-600 sm:flex-row">
          <span>&copy; {new Date().getFullYear()} DealProof.</span>
          <Link to="/report" className="text-slate-400 hover:text-slate-200">
            View a sample report &rarr;
          </Link>
        </div>
      </footer>
    </div>
  )
}
