# DealProof

**AI-native due-diligence red-flag analysis for small-business acquisitions.**
Upload the data room, get an institutional-grade red-flag report — where to dig
before you spend $50k on a CPA or walk away.

DealProof is a **red-flag scanner and diligence accelerant**. It is *not* a CPA
firm, *not* a Quality of Earnings engagement, and *not* financial, legal, tax, or
valuation advice. It produces findings, evidence, and questions — never a score
or a buy/don't-buy recommendation. (See `SPEC.md` §8.)

---

## What's in this repo

```
backend/    FastAPI + the deterministic reconciliation & rules engine (Python)
frontend/   React + TypeScript + Vite + Tailwind — the report UI & marketing site
infra/      nginx reverse proxy config
docker-compose.yml, Makefile, SPEC.md, DECISIONS.md
```

The heart of the product is the **deterministic engine** (`backend/app/engine` +
`backend/app/rules`): pure-stdlib `Decimal` math that cross-verifies every
financial claim across tax returns, internal P&Ls, and bank statements (the
**Triangle of Truth**), then fires a versioned, data-driven library of red-flag
rules. The LLM extracts and narrates; **Python does every number that reaches the
report**, and every number is traceable to a source document page.

## Quick start (one command)

```bash
cp .env.example .env
docker compose up --build      # or: make up
# open http://localhost:8080
```

On startup the API creates its schema and **seeds a live sample**: a synthetic
HVAC deal ("Project Summit") with a fully-rendered, published, paywall-unlocked
red-flag report — so the marketing site's sample report and the app both work on
first boot, offline, with no API keys.

Set `ANTHROPIC_API_KEY` in `.env` to switch report narration from the
deterministic template backend to Claude (still guarded by the grounding check).

## Local development (no Docker)

```bash
# Backend engine + API tests (pure-stdlib core needs nothing but pytest)
cd backend && python -m pytest -q

# Regenerate the demo report + synthetic source PDFs
python -m app.seeder.export          # or: make seed-demo

# Run the API on SQLite
uvicorn app.main:app --reload        # http://localhost:8000/docs

# Frontend
cd frontend && npm install && npm run dev
```

## Tests — the accuracy story

```bash
cd backend && python -m pytest -q     # 106 tests
```

- **Money & reconciliation** — Decimal rounding, Triangle math, missing-source
  handling (no false zeros).
- **Rules engine** — every one of the 17 rules has a *fire* case **and** a
  *no-fire* case (a false positive is the worst outcome for this product).
- **Golden demo** — asserts the seeded HVAC deal fires **exactly** the 6 planted
  red flags (4 CRITICAL, 2 HIGH) plus the INFO benchmark, with **no CRITICAL
  false positives**.
- **Traceability** — every evidence citation resolves to a real document page.
- **Grounding** — hallucinated numbers in narration are caught and rejected.
- **Extraction** — real PDF bytes → classify → extract → report, asserting the
  extracted numbers match the source pages and the six flags still fire.
- **API smoke + full lifecycle** — the app boots, seeds, and drives
  create → upload PDFs → process → publish → pay → unlocked report, enforcing
  org isolation + the payment paywall.

## The pipeline (SPEC §2.3)

```
Stage 0 Intake  → 1 Classify → 2 Extract → 3 Reconcile (deterministic Python)
              → 4 Flag (rules engine) → 5 Narrate (grounded LLM) → 6 QA (human)
              → 7 Deliver (web report + PDF + seller questions + data gaps)
```

Reports are **not visible to buyers until an admin publishes** (Stage 6 human
review) and payment unlocks them. See `SPEC.md` for the full specification and
`DECISIONS.md` for what is production-real vs. scaffolded in this iteration.

## Pricing (SPEC §6)

| Tier | Price |
|---|---|
| Snapshot | $499 |
| Full Diligence Report | $2,950 / deal |
| Deal Desk (serial acquirers) | $1,500/mo + $1,950 / deal |
| Broker White-Label | $6k/yr + $1,750 / deal |
