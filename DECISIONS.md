# DECISIONS — DealProof v1

Engineering decisions made while building Iteration 1, and why. Kept honest:
what is production-real, what is scaffolded, and what is deferred.

## Architecture

1. **The deterministic core is pure stdlib (Decimal + dataclasses).**
   The reconciliation engine (`app/engine`) and rules engine (`app/rules`) import
   no third-party packages. Consequences: the accuracy-critical code has zero
   dependency surface, its 60+ tests run in ~0.1s in a bare interpreter, and the
   "LLM extracts, Python computes" boundary (SPEC §2.3) is physically enforced —
   the engine literally cannot call an LLM.

2. **Money is `Decimal`, never `float`.** `app/engine/money.py` refuses floats at
   the boundary (`money(1.23)` raises). Percentages and multiples are computed one
   way, everywhere. Division-by-zero returns `None` (a documented "no basis"),
   never a misleading `0`.

3. **Rules are data, interpreted by code (SPEC §2.2/§5).** Each rule is a
   `RuleDef` (id, version, category, `kind`, thresholds, vertical overrides) —
   the same shape as a `flag_rules` DB row. `evaluators.py` interprets `kind` +
   thresholds. This is what lets the pattern library be CRUD-edited, versioned,
   and back-tested without a deploy. Thresholds are copied verbatim from the spec.

4. **v1 ships 17 rules**: the 15 named in the build prompt
   (A1 A2 A4 A5 B9 B10 B12 B14 C17 C18 C21 C22 D24 D25 G39) plus the two Triangle
   of Truth reconciliation rules (TT1 tax-vs-P&L divergence, TT2 bank-deposit
   shortfall) from SPEC §2.1 — the core differentiator. The remaining ~25 flags in
   the spec's library are defined in `SPEC.md` and are additive `RuleDef`s.

5. **Grounding is enforced mechanically, not by prompt (SPEC §2.3, §8).**
   `assert_grounded()` scans generated prose for numeric tokens and rejects any
   not present in the evidence bundle (years and small counts are allowed as
   prose). The narrator retries on violation and falls back to a deterministic
   template rather than ship an ungrounded number. This is the accuracy story and
   the liability story in one function.

6. **No composite score, ever (SPEC §8).** The report exposes severity *counts*,
   never an aggregate score or buy/don't-buy output. Encoded in the report
   assembler and the disclaimer module.

7. **Offline-by-default demo.** With no `ANTHROPIC_API_KEY`, the narrator uses the
   template backend, so `make seed-demo` and `docker compose up` produce a full,
   grounded report on a clean clone with no network and no keys. Set the key to
   switch Stage 5 to Claude (guarded by the same grounding check).

## Trade-offs / scope

8. **Auth uses stdlib HMAC tokens, not JWT.** Avoids a `cryptography` native
   dependency (and a real build panic seen in this environment). Magic-link +
   session tokens are HMAC-SHA256 signed. TOTP is a column, not yet wired.

9. **SQLite in dev, Postgres in prod.** Models use portable `JSON` + `Numeric`, so
   the same schema runs on SQLite (tests, local) and Postgres 16 (compose). The
   API `create_all()` + demo bootstrap on startup is a dev convenience; production
   uses the Alembic scaffold (`backend/alembic`) + a seed command.

10. **Synthetic source PDFs via a stdlib PDF writer** (`app/services/pdfgen.py`),
    not WeasyPrint, so the demo has real, browsable documents for the evidence
    drawer with nothing installed. Production *report* PDFs use WeasyPrint from a
    print-CSS template (dependency declared; template is a v1.1 item).

11. **Pipeline stages 0–2 (intake/classify/extract) are implemented end-to-end.**
    `app/pipeline/{intake,classify,extract,ingest}.py` take raw PDF bytes →
    SHA-256 dedupe → classification → structured extraction into
    `financial_lines` + facts (each with page citations) → `DealContext`, sharing
    the Stage 3–5 code path with the demo. An offline heuristic classifier/
    extractor parses the data-room documents so the whole pipe runs without an
    API key; the Claude path uses the versioned prompts. The upload/process API
    (`app/api/routers/documents.py`) drives it, and a test asserts extracted
    numbers match the source pages.

12. **Report PDF via WeasyPrint** (`app/services/report_pdf.py`): `build_html`
    is pure and tested; `render_pdf` lazily imports WeasyPrint (native libs
    installed in the backend image). Disclaimer runs in the page footer on every
    page. The synthetic *source* documents still use the stdlib writer.

13. **Data-quality dimension (inaccurate inputs).** Because the product exists
    for *untrustworthy* seller data, a "Data Quality" rule category (DQ1–DQ4)
    flags when the figures themselves are implausible or uncrossable: fewer than
    two independent revenue sources (can't triangulate), COGS exceeding revenue
    (negative gross profit), non-positive revenue, and deposits far exceeding
    revenue (loans/transfers mislabeled as sales). These fire only on bad data
    and stay silent on the valid demo.

14. **Fail-soft pipeline.** `run_rules(strict=False)` (used by the pipeline)
    skips and records any evaluator that trips on malformed input rather than
    aborting — one bad figure can't sink the report. `strict=True` (tests)
    still surfaces regressions. Extraction/ingest tolerate empty, corrupt, and
    non-PDF bytes (no text → no lines → everything becomes a data gap, no crash).
    Covered by `tests/test_bad_inputs.py` (garbage bytes, zero/negative/huge
    figures, contradictory duplicates, single-source deals, broken-rule
    injection). 120 tests total.

## What is deferred (documented, not hidden)

- Extraction coverage: the offline parser targets the standard statement layouts;
  arbitrary real-world PDFs rely on the Claude extractor (prompts shipped) and
  benefit from broader few-shot coverage over time.
- QuickBooks/Plaid imports (SPEC §4 v2); Ask-the-Deal chat (SPEC §3.8, v1.5).
- ClamAV/MinIO are in compose and wired at the storage/config layer; upload
  virus-scan is a boundary hook not yet exercised end-to-end.
