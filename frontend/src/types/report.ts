// Typed subset of the DealProof report contract (frontend/public/demo_report.json).
// Amounts are numeric strings in the source data — parse with Number() before formatting.

export type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'INFO'

export interface Deal {
  codename: string
  entity_name: string
  vertical: string
  // Present on the static demo sample; API-produced reports only carry the raw
  // `vertical` slug, so consumers fall back to lib/vertical.ts#verticalLabel.
  vertical_label?: string
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
  // Optional: a deal's vertical may have no seeded benchmark yet.
  sde_multiple?: SdeMultipleBenchmark
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
  // The static demo sample carries a human title/filename; API-produced
  // reports (assembled from the `/process` pipeline) only carry doc_type,
  // period, page_count, confidence, and a storage url — so these are optional.
  title?: string
  doc_type: string
  period: number
  page_count: number
  filename?: string
  confidence?: number
  url: string
}

export interface ClauseFinding {
  clause_type: string
  label: string
  severity: Severity
  counterparty: string
  doc_type: string
  quote: string
  risk: string
  buyer_action: string
  source: EvidenceRef
}

export interface ContractReviewEntry {
  document_id: string
  counterparty: string
  doc_type: string
  findings: ClauseFinding[]
  highest_severity: Severity
}

export interface ContractReview {
  documents_reviewed: number
  clauses_flagged: number
  severity_summary: SeverityCounts
  contracts: ContractReviewEntry[]
  note: string
}

export interface PacketSection {
  heading: string
  items: string[]
}

export interface ExpertPacket {
  key: string
  audience: string
  title: string
  purpose: string
  sections: PacketSection[]
  questions: string[]
}

export interface ExpertPackets {
  qofe: ExpertPacket
  attorney: ExpertPacket
  lender: ExpertPacket
}

export interface DealProofReport {
  deal: Deal
  completeness_score: number
  watermark: string | null
  severity_counts: SeverityCounts
  triangle: TrianglePeriod[]
  flags: Flag[]
  normalization: Normalization
  contract_review?: ContractReview | null
  expert_packets?: ExpertPackets | null
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
  verification?: Verification | null
  workstreams?: Workstream[]
}

export interface Verification {
  document_count: number
  avg_confidence: number
  low_confidence: { doc_type: string; confidence: number }[]
  reliable: boolean
}

export interface Workstream {
  key: string
  title: string
  description: string
  coverage: 'automated' | 'partial' | 'guided' | 'roadmap'
  coverage_label: string
  findings: { rule_id: string; severity: string; title: string }[]
  finding_count: number
  checklist: string[]
  note?: string
  interview_targets?: {
    name: string
    revenue: string
    share_pct: string | null
    script: string[]
  }[]
}
