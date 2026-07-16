"""Fixed liability language (SPEC §8). This exact text appears on every report
page footer, in the ToS, and in the API's report payload. Do not paraphrase."""

DISCLAIMER = (
    "DealProofing is an automated document-screening and red-flag identification "
    "tool, not a substitute for professional diligence. It does not provide "
    "accounting, legal, tax, investment, or valuation advice; is not a CPA firm, "
    "law firm, or broker-dealer; and does not perform a Quality of Earnings "
    "engagement, an audit, or a legal opinion. Findings are generated from the "
    "documents supplied, may contain errors or omissions, and are only as "
    "accurate as those documents. They identify areas for review by your own "
    "qualified CPA, attorney, and lender, who remain responsible for the "
    "decision to proceed. Nothing here is a recommendation to buy or not buy."
)

# The product never emits a composite score, pass/fail, or buy/don't-buy output.
NO_SCORE_POLICY = (
    "DealProof intentionally produces no single score and no recommendation — "
    "only findings, evidence, and questions."
)
