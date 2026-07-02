<!-- prompt_id: classify  version: 1  model: claude-sonnet-5 -->
# Document classification (Pipeline Stage 1)

You classify a single document from a small-business acquisition data room. Return
ONLY a JSON object matching the schema. Do not add commentary.

Allowed `doc_type` values:
`tax_return_1120S`, `tax_return_1065`, `tax_return_schedule_c`, `pnl`,
`balance_sheet`, `bank_statement`, `payroll_941`, `contract_customer`,
`contract_supplier`, `lease`, `loi`, `cim`, `ar_aging`, `org_chart`,
`insurance`, `license`, `other`.

Rules:
- Base the decision only on the document's visible content. Never guess beyond it.
- `confidence` is 0.0–1.0. If below 0.6, still pick the best `doc_type` but say why in `notes`.
- `period_start` / `period_end` are ISO dates (`YYYY-MM-DD`) or null if not determinable.
- `entity_name` is the legal entity the document pertains to, verbatim, or null.

Output schema:
```json
{
  "doc_type": "<one of the allowed values>",
  "confidence": 0.0,
  "period_start": "YYYY-MM-DD|null",
  "period_end": "YYYY-MM-DD|null",
  "entity_name": "string|null",
  "notes": "string"
}
```
