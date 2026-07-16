# Production readiness & liability posture

DealProofing is built to be **safe as a screening tool**, and deliberately
honest about the line between *demo-grade* and *charge-real-money-grade*. This
document is the checklist that must be green before a buyer pays for a report
they will act on. It is intentionally blunt.

## Status legend
- ✅ **Done in code** — implemented and tested in this repo.
- ⚙️ **Config / deployment** — the code supports it; it must be switched on per environment.
- ⚖️ **Human / legal** — cannot be solved in code; requires a professional.

---

## Security & data protection

| Item | Status | Notes |
|---|---|---|
| Confidential documents behind signed, short-lived links | ✅ | HMAC storage tokens (`SIGNED_URL_TTL_SECONDS`, default 15 min). No unauthenticated document access. |
| Org-scoped access to every deal/report | ✅ | `get_scoped_deal`; cross-org access 404s. |
| Append-only audit log | ✅ | Every upload/process/publish/pay/attest/purge recorded. |
| Buyer data-purge + signed deletion certificate | ✅ | `DELETE /deals/{id}/data`; certificate id from the audit row. |
| Upload safety gate (content validation) | ✅ | Rejects non-PDF, oversized, and renamed executables/archives before storage or parsing. `MAX_UPLOAD_MB`. |
| Malware scan (fail-closed) | ✅ code / ⚙️ daemon | EICAR always caught; ClamAV wired via `CLAMAV_HOST`/`CLAMAV_PORT` when a `clamd` daemon is provisioned. Without it, content validation is the guard. |
| Magic-link token never exposed in production | ✅ | Token only returned when `ENV != production`; production requires a working email provider or the request 503s. |
| Transactional email delivery | ✅ code / ⚙️ key | Resend via `RESEND_API_KEY`; logs in dev. |
| Encryption at rest | ⚙️ | Enable on the managed Postgres and object store (S3 SSE / provider-managed keys). No secrets in the repo. |
| Secrets management | ⚙️ | `JWT_SECRET`, `STRIPE_*`, `RESEND_API_KEY` set via the platform's secret store — never committed. Default `JWT_SECRET` is dev-only and must be overridden. |
| Rate limiting / WAF on public endpoints | ⚙️ | Terminate at the platform edge (auth/request especially). |

## Accuracy & correctness

| Item | Status | Notes |
|---|---|---|
| Pure-Decimal money engine (no floats) | ✅ | `money()` rejects floats; reconciliation is exact. |
| Grounded narration (no fabricated numbers) | ✅ | `assert_grounded`; deterministic template fallback offline. |
| Deterministic rule library + contract clause scanner | ✅ | 46 rules + clause catalog; every finding cites a page. |
| Fail-soft pipeline on bad/inaccurate data | ✅ | `run_rules(strict=False)`; data-quality flags (DQ1–DQ4); extraction tolerates garbage/empty/corrupt PDFs. |
| Extraction-confidence surfaced to the buyer | ✅ | Verification strip; low-confidence documents flagged. |
| **Human QA before a report reaches a buyer** | ⚖️ + ✅ gate | Publishing is an explicit admin action (`/admin/deals/{id}/publish`); a qualified human should review every report before publish. The gate exists; the human is a staffing commitment. |
| Software-target modules (code/user audits) | 🚫 roadmap | Deliberately **not** faked. Shown as roadmap. A shallow SCA gives false confidence and is a liability — do not enable until a real scanner is wired. |

## Legal & positioning

| Item | Status | Notes |
|---|---|---|
| "Screening tool, not advice/audit" disclaimer on every surface | ✅ | Report footer (every PDF page), API payload, ToS. |
| No composite score / no buy-recommendation | ✅ | `NO_SCORE_POLICY` — findings, evidence, questions only. |
| Confidentiality / NDA posture (attestation + provable deletion) | ✅ | Buyer confidentiality attestation + deletion certificate for the seller. |
| **Attorney-reviewed Terms of Service & report disclaimer** | ⚖️ | The language here is drafted defensively but must be reviewed by counsel before charging. |
| **NDA fit is the buyer's responsibility** | ⚖️ | The product supplies the controls; it cannot read the buyer's specific NDA. State this plainly in the ToS. |

---

## The one-line summary

The **engine and the confidentiality/security controls are production-real and
tested.** Before taking real money, the remaining gates are almost entirely
**operational, not code**: turn on encryption-at-rest and a ClamAV daemon,
provision the email/secret config, staff human QA on the publish step, and have
counsel review the ToS. Sold as *analyst-reviewed red-flag screening with expert
hand-off* — with honest disclaimers — DealProofing is an asset. Sold as *"AI that
replaces your CPA and attorney,"* it is a lawsuit. The code is built to support
the first framing and to refuse the second.
