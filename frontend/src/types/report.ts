// Typed subset of the DealProof report contract (frontend/public/demo_report.json).
// Amounts are numeric strings in the source data — parse with Number() before formatting.

export type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'INFO'

export interface Deal {
  codename: string
  entity_name: string
  vertical: string
  vertical_label: string
  state: string
  deal_type: string
  asking_price: string
  claimed_sde: string
  stage: string
  tier: string
}

export interface SeverityCounts {
  CRITICAL: number
  HIGH: number
  MEDIUM: number
  INFO: number
}

export interface TriangleSource {
  document_id: string
  page: number
  label: string
}

export interface TrianglePeriod {
  period: number
  tax_revenue: string
  pnl_revenue: string
  bank_deposits: string
  tax_vs_pnl_divergence_pct: string
  deposit_coverage_pct: string
  sources?: TriangleSource[]
}

export interface EvidenceRef {
  document_id: string
  page: number
  label: string
}

export interface FlagNarrative {
  rule_id: string
  finding: string
  why_it_matters: string
}

export interface Flag {
  rule_id: string
  rule_version: number
  category: string
  severity: Severity
  title: string
  detail: string
  computed_values: Record<string, string | number>
  evidence_refs: EvidenceRef[]
  buyer_action: string
  ask_seller: string[]
  what_resolves: string
  narrative: FlagNarrative
}

export interface NormalizationRow {
  description: string
  amount: string
  category: string
  verdict: 'Verified' | 'Undocumented' | 'Review' | string
  source: EvidenceRef
}

export interface Normalization {
  claimed_sde: string
  adjusted_sde: string
  removed_undocumented: string
  rows: NormalizationRow[]
  note: string
}

export interface SdeMultipleBenchmark {
  metric: string
  p25: string
  p50: string
  p75: string
  n_deals: number
  source: string
}

export interface Benchmarks {
  sde_multiple: SdeMultipleBenchmark
}

export interface DataGap {
  key: string
  label: string
}

export interface SellerQuestion {
  rule_id: string
  severity: Severity
  question: string
}

export interface ReportDocument {
  id: string
  title: string
  doc_type: string
  period: number
  page_count: number
  filename: string
  url: string
}

export interface DealProofReport {
  deal: Deal
  completeness_score: number
  watermark: string | null
  severity_counts: SeverityCounts
  triangle: TrianglePeriod[]
  flags: Flag[]
  normalization: Normalization
  benchmarks: Benchmarks
  data_gaps: DataGap[]
  seller_question_pack: SellerQuestion[]
  executive_summary: string[]
  narrative: {
    executive_summary: string[]
    flag_narratives: FlagNarrative[]
    data_gaps_intro: string
    closing_note: string
  }
  disclaimer: string
  documents: ReportDocument[]
}
