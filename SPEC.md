# DealProof — Master Product Specification

**Status:** canonical reference. This document is the single source of truth
that the codebase implements and cross-references (e.g. `SPEC §2.1`,
`SPEC §8`). If code and this document disagree, this document wins until it
is explicitly updated.

---

## 1. Product Summary

DealProof is an AI-native due-diligence platform for buyers (and their
advisors) evaluating the acquisition of a small/lower-middle-market business
("main street" through ~$20M revenue deals). A buyer uploads the seller's
diligence package — tax returns, internal financial statements (P&L, balance
sheet), bank statements, contracts, leases, cap tables, and other supporting
documents — and DealProof produces a structured, evidence-linked findings
report: cross-verified financials, a red-flag list drawn from a fixed rule
library, and a narrated summary, all with every number traceable back to the
source page it came from.

DealProof is explicitly **not** a replacement for a CPA-led Quality of
Earnings (QoE) engagement, legal counsel, or a licensed valuation. It is a
fast, consistent, first-pass diligence layer that surfaces the questions a
buyer should be asking before they pay for those engagements — see §8 for the
liability architecture that keeps this boundary hard-coded into the product.

---

## 2. Core Methodology

### 2.1 The Triangle of Truth

The foundational analysis DealProof performs on every deal is a three-way
cross-verification of claimed revenue, because a seller narrative and a
single financial statement can both be wrong (or dressed up) in the same
direction. DealProof reconciles revenue across three independent sources that
are very hard to simultaneously falsify:

1. **Tax returns** (filed with a taxing authority — the number a seller has
   the least incentive to inflate),
2. **Internal P&L / financial statements** (the number sellers usually use to
   market the deal — the number with the most incentive to inflate), and
3. **Bank statements** (actual cash deposited — the hardest number to fake,
   since it requires either real transactions or a conspiracy with a bank).

This reconciliation is **fully deterministic** — it runs in pure Python
(`app/engine/reconcile.py`) on structured, extracted line items. No LLM is
involved in computing it (see §2.3, Stage 3).

**Thresholds:**

| Check | Condition | Result |
|---|---|---|
| Tax vs. P&L divergence | `abs(tax_revenue − pnl_revenue) / pnl_revenue > 5%` | Flag raised (rule **TT1**) — severity scales with the size of the gap (see rule table, §2.2) |
| Bank deposit coverage | `bank_deposits / reported_revenue < 92%` | **HIGH** severity (rule **TT2**) |
| Bank deposit coverage | `bank_deposits / reported_revenue < 80%` | **CRITICAL** severity (rule **TT2**) |

Deposit coverage below 92% means more than 8 cents of every claimed revenue
dollar never hit a bank account DealProof can see; below 80% is treated as a
critical, deal-threatening gap that must be explained (undisclosed accounts,
cash-pay not banked, timing lag, or the revenue simply isn't real) before the
buyer proceeds.

The Triangle of Truth is DealProof's core differentiator: every other section
of the report (add-back analysis, benchmarking, narrative) is built on top of
a revenue figure that has already been cross-verified this way.

### 2.2 The Red Flag Library

Findings are produced by a versioned, data-driven rule library (not
hardcoded branching logic) so it can be extended and back-tested from the
admin console (§5) without a code deploy. Each rule is a row with an `id`,
`category`, evaluator `kind`, `thresholds`, default `severity`, buyer-facing
copy (`buyer_action`, `ask_seller` questions, `what_resolves`), and an
`active` flag. Severities are **CRITICAL**, **HIGH**, **MEDIUM**, or **INFO**.

The full v1 library spans **40 flags** across seven categories, **A–G**:

#### Category A — Revenue Quality

| ID | Title | Default Severity |
|---|---|---|
| A1 | Customer concentration risk (top customer share of revenue) | HIGH |
| A2 | Trailing-12-month revenue decline masked by annual totals | HIGH |
| A3 | Seasonal revenue concentration understated in annual summary | MEDIUM |
| A4 | One-time revenue treated as recurring (PPP/ERC/grants/asset sales) | HIGH |
| A5 | Single-channel revenue dependency (marketplace/platform risk) | HIGH |
| A6 | Undisclosed related-party revenue | HIGH |
| A7 | Revenue recognition inconsistent across periods | MEDIUM |
| A8 | Pipeline/backlog claims unsupported by signed contracts | MEDIUM |

#### Category B — Earnings Quality

| ID | Title | Default Severity |
|---|---|---|
| B9 | Add-backs are a large share of claimed earnings | HIGH |
| B10 | Undocumented "personal expense" add-backs | MEDIUM |
| B11 | Owner-compensation add-back inconsistent with replacement-labor cost | MEDIUM |
| B12 | Below-market rent (seller owns the operating real estate) | HIGH |
| B13 | Related-party expenses removed as add-backs without market comparison | MEDIUM |
| B14 | Capex starvation (capex below depreciation for 2+ consecutive years) | HIGH |
| B15 | Inventory valuation inconsistent between statements and count | MEDIUM |
| B16 | Gross margin trend diverges from stated pricing/cost story | MEDIUM |

#### Category C — Cash & Balance Sheet

| ID | Title | Default Severity |
|---|---|---|
| C17 | Negative or declining working capital | MEDIUM |
| C18 | Aged accounts receivable (>90 days past due, material share) | HIGH |
| C19 | Accounts payable stretching / vendor-terms deterioration | MEDIUM |
| C20 | Undisclosed debt or liens found in bank feed or filings | HIGH |
| C21 | Overdraft / NSF events in bank statements | MEDIUM |
| C22 | Merchant cash advance / factoring detected (hidden distress signal) | CRITICAL |
| C23 | Balance sheet does not tie between periods (unexplained equity jump) | HIGH |

#### Category D — Legal & Contracts

| ID | Title | Default Severity |
|---|---|---|
| D24 | Change-of-control clause in a key contract (deal killer) | CRITICAL |
| D25 | Lease risk: short remaining term, no assignment, or personal guarantee | HIGH |
| D26 | Pending or historical litigation not disclosed upfront | HIGH |
| D27 | Key contracts missing, expired, or unsigned | MEDIUM |
| D28 | Non-compete / non-solicit gaps that expose post-close competition | MEDIUM |
| D29 | IP ownership unclear (contractor-built assets, no assignment) | HIGH |
| D30 | Licenses/permits not transferable or near expiration | HIGH |

#### Category E — People & Ops

| ID | Title | Default Severity |
|---|---|---|
| E31 | Key-person dependency (owner or single employee is the business) | HIGH |
| E32 | Undocumented related-party employees on payroll | MEDIUM |
| E33 | Unusual employee turnover in the trailing 12 months | MEDIUM |
| E34 | Missing or inconsistent employment agreements for key staff | MEDIUM |

#### Category F — Tax & Compliance

| ID | Title | Default Severity |
|---|---|---|
| F35 | Payroll tax filings inconsistent with reported headcount/wages | HIGH |
| F36 | Sales tax collected vs. remitted mismatch | HIGH |
| F37 | Worker misclassification risk (1099s doing W-2 work) | MEDIUM |
| F38 | Open or unresolved tax authority correspondence/audit | CRITICAL |

#### Category G — Deal Structure

| ID | Title | Default Severity |
|---|---|---|
| G39 | Asking multiple materially above the vertical benchmark | INFO |
| G40 | Deal structure (asset vs. stock) creates disclosed but unpriced risk | MEDIUM |

**v1 launch subset:** the current engine implements the two Triangle of Truth
rules (**TT1**, **TT2** — §2.1) plus 15 of the 40 catalog flags:
`A1, A2, A4, A5, B9, B10, B12, B14, C17, C18, C21, C22, D24, D25, G39`. The
remaining catalog rules are defined in this specification and the admin
pattern library (§5) as the backlog for subsequent rule releases; the
`flag_rules` schema and evaluator interface are built to accept them without
a data-model change.

Every fired flag carries: `rule_id`, `rule_version`, `category`, `severity`,
a one-line `title`, a number-bearing `detail`, `computed_values`,
`evidence_refs` (page-level citations — see §2.3's grounding rule), a
`buyer_action`, a list of `ask_seller` questions, and a `what_resolves`
description of the evidence that would clear the flag.

### 2.3 The Claude Orchestration Pipeline

Every deal moves through eight stages. The critical architectural rule,
enforced end-to-end, is:

> **LLM extracts, Python computes, LLM narrates grounded — every number
> traces to evidence.**

Claude is never trusted to do arithmetic that ends up in a report, and no
narrative sentence is allowed to contain a number that cannot be traced back
to a specific extracted fact and its source page.

| Stage | Name | What happens |
|---|---|---|
| 0 | **Intake** | Documents are uploaded, virus-scanned (ClamAV), stored (S3-compatible object storage), and registered against the deal. |
| 1 | **Classify** | Claude classifies each document (tax return, P&L, balance sheet, bank statement, contract, lease, etc.) and identifies period/year coverage. |
| 2 | **Extract** | Claude extracts structured line items, facts, and figures from each document, each tagged with a `PageRef` (document id + page number) pointing at the exact source location. |
| 3 | **Reconcile** | **Deterministic Python, no LLM.** The Triangle of Truth (§2.1) and all downstream money math run in `app/engine/*` using fixed-point `Decimal` arithmetic — never floating point, never an LLM guess. |
| 4 | **Flag** | The rule engine (`app/rules/engine.py`) evaluates the full `DealContext` (reconciliation result + extracted facts) against the active rule library (§2.2) and emits `Flag` objects, purely data-driven. |
| 5 | **Narrate** | Claude writes the human-readable summary and per-flag narrative — **grounded**: every number and claim in the narrative must be present in the evidence bundle assembled from Stages 3–4, or generation is rejected/retried. An offline template narrator produces the same structure without calling the LLM when `ANTHROPIC_API_KEY` is unset, so the pipeline is fully testable and demoable without API access. |
| 6 | **QA / human review** | A human reviewer works the admin review queue (§5) against every report before delivery: verifying flags, editing narrative, and applying QA labels that build the training/pattern-library moat. No report reaches a buyer unreviewed. |
| 7 | **Deliver** | The reviewed report is rendered (web + PDF), the buyer is notified, and the report + underlying evidence bundle become available via signed, time-limited URLs. |

Because Stage 3 (the only stage that touches money math) has zero LLM
involvement, the reconciliation and every flag's `computed_values` are
reproducible byte-for-byte from the same inputs — this is what makes the
engine unit-testable with golden fixtures (see `backend/tests/`) and what
makes the "every number traces to evidence" guarantee enforceable in Stage 5.

---

## 3. Users & Roles

- **Buyer** — uploads/owns deals, purchases and receives reports.
- **Broker / Advisor** — can run deals on behalf of clients (white-label tier, §6).
- **Analyst / QA reviewer** — internal role; works the admin review queue (§5).
- **Admin** — manages the rule library, benchmarks, users, and orgs.

---

## 4. Deal Lifecycle

A deal moves from creation → document intake → pipeline run (§2.3) → QA
review → delivery → (optional) re-run when new documents arrive or a
correction is needed. Deals belong to an org; orgs may be a single buyer, a
brokerage, or a "deal desk" subscription account (§6).

---

## 5. Admin Console

Internal-only console used by analysts and admins:

- **Review queue** — every report generated by the pipeline lands here before
  delivery. Reviewers see the full evidence bundle, extracted facts, fired
  flags, and generated narrative side by side with the source documents;
  they can edit narrative text, adjust/override flag severity, add manual
  findings, and approve for delivery.
- **QA labels (moat table)** — every reviewer action (approve/edit/reject
  a flag or narrative sentence, mark a false positive/negative, correct an
  extraction) is captured as a structured `qa_labels` row. This labeled
  dataset is the long-term data moat: it is used to tune extraction prompts,
  tighten rule thresholds, and eventually train/fine-tune classification and
  extraction quality — independent of any single LLM vendor.
- **Pattern library manager** — CRUD interface over the `flag_rules` table
  (§2.2): create/version/retire rules, edit thresholds and vertical
  overrides, toggle `active`, and back-test a proposed rule change against
  historical deals before it goes live.

---

## 6. Pricing

| Product | Price |
|---|---|
| **Snapshot** — quick triangulated-revenue + top flags check | $499 (one-time) |
| **Full Report** — complete red-flag report across all categories with narrative | $2,950 (one-time) |
| **Deal Desk** — subscription for active buyers/funds running multiple deals | $1,500/mo + $1,950 per deal |
| **Broker White-Label** — branded reports for brokerages to offer their sellers/buyers | $6,000/yr + $1,750 per deal |
| **Rush** — expedited turnaround add-on on any tier | +$750 |
| **Re-run** — re-run the pipeline on an existing deal (new/corrected documents) | $450 |

---

## 7. Technical Architecture

**Frontend:** React + TypeScript + Tailwind CSS, built with Vite, served as a
static bundle behind Nginx.

**Backend:** FastAPI on Python 3.12, with a pure-Python, dependency-free
deterministic engine (`app/engine`, `app/rules`) at its core so the financial
math and rule evaluation can be fully unit-tested without a database,
network, or LLM call.

**Datastores / infra:**

- **PostgreSQL 16** — primary relational store.
- **Redis + Celery** — task queue for async pipeline runs (document
  processing, LLM calls, PDF generation).
- **S3-compatible object storage** (MinIO in dev/self-hosted, S3 in
  production) — source documents, generated PDFs, evidence bundles.
- **Nginx** — reverse proxy in front of the static frontend and the API.
- **ClamAV** — malware scanning of every uploaded document at intake
  (Stage 0).
- **Docker Compose** — local/dev orchestration of all of the above.

**Core data model (tables):**

| Table | Purpose |
|---|---|
| `users` | Authenticated individuals (buyers, brokers, analysts, admins). |
| `orgs` | Buyer/brokerage/deal-desk accounts; billing + plan tier lives here. |
| `deals` | One acquisition target under diligence; owns documents/reports. |
| `documents` | Uploaded files: type, classification (Stage 1), storage key, scan status. |
| `extractions` | Structured output of Stage 2 extraction per document, with page-level refs. |
| `financial_lines` | Normalized `FinancialLine` rows (period, statement type, line code, amount) feeding Stage 3 reconciliation. |
| `flags` | Fired `Flag` rows per deal (rule id/version, severity, evidence refs, buyer copy). |
| `flag_rules` | The versioned rule library (§2.2/§5) — data, not code. |
| `reports` | Assembled report payloads/PDFs per deal, with QA/delivery status. |
| `qa_labels` | Reviewer actions/corrections from the admin review queue (§5) — the training-data moat. |
| `benchmarks` | Vertical financial benchmarks (e.g. SDE multiples) used by rules like G39. |
| `audit_log` | Immutable record of who did what, when, across the system. |
| `payments` | Orders/subscriptions/invoices mapped to the pricing tiers in §6. |

---

## 8. Liability Architecture

DealProof is deliberately engineered — in product copy, in the API, and in
report rendering — to stay on the safe side of "diligence support tool," not
"advice." This is enforced in code, not just policy:

- **Fixed disclaimer language** appears on every report page footer, in the
  Terms of Service, and in the API's report payload, verbatim
  (`app/core/disclaimer.py`), and must not be paraphrased:

  > "DealProof is an automated document-analysis and red-flag identification
  > tool. It does not provide accounting, legal, tax, investment, or
  > valuation advice; is not a CPA firm; and does not perform a Quality of
  > Earnings engagement. Findings identify areas for further professional
  > review."

- **No composite score, no buy/don't-buy output.** The product never emits a
  single overall score, a pass/fail verdict, or a recommendation to proceed
  or walk away — only findings, evidence, and questions to ask the seller.
  This is a hard product rule, not a UI choice:

  > "DealProof intentionally produces no single score and no recommendation
  > — only findings, evidence, and questions."

- **Human QA on every report.** No report reaches a buyer without passing
  through the admin review queue (§5, Stage 6) — a human reviewer has always
  seen and approved the specific findings and narrative before delivery.

Together, the Triangle of Truth's deterministic math (§2.1/§2.3), the
grounded-narrative guarantee (every number traces to evidence), and this
liability architecture are what let DealProof make strong, specific claims
about financial red flags while remaining, by design, a document-analysis
tool rather than a licensed advisory service.
