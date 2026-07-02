"""Fixed liability language (SPEC §8). This exact text appears on every report
page footer, in the ToS, and in the API's report payload. Do not paraphrase."""

DISCLAIMER = (
    "DealProof is an automated document-analysis and red-flag identification "
    "tool. It does not provide accounting, legal, tax, investment, or valuation "
    "advice; is not a CPA firm; and does not perform a Quality of Earnings "
    "engagement. Findings identify areas for further professional review."
)

# The product never emits a composite score, pass/fail, or buy/don't-buy output.
NO_SCORE_POLICY = (
    "DealProof intentionally produces no single score and no recommendation — "
    "only findings, evidence, and questions."
)
