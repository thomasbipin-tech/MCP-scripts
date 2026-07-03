// Typed shapes for the live FastAPI backend (distinct from the static
// demo_report.json contract in types/report.ts, though the two overlap for
// the report body — see DealProofReport).

import type { DealProofReport, SeverityCounts } from './report'

export interface AuthUser {
  id: string
  email: string
  role: string
  org_id: string
}

export interface MagicRequestResponse {
  sent: boolean
  email: string
  magic_token?: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

// GET /deals, GET /deals/{id}, POST /deals response shape.
export interface DealSummary {
  id: string
  codename: string
  entity_name: string | null
  vertical: string
  state: string | null
  asking_price: string | null
  claimed_sde: string | null
  deal_type: string
  stage: string
  completeness_score: number
  tier: string
  paid: boolean
  severity_counts: SeverityCounts
  report_published: boolean
}

export interface DealCreatePayload {
  codename: string
  vertical: string
  state?: string
  asking_price?: string
  claimed_sde?: string
  deal_type?: string
  entity_name?: string
  tier?: string
}

// GET /deals/{id}/documents item.
export interface DocumentInfo {
  id: string
  doc_type: string
  confidence: number | null
  page_count: number
  entity_name: string | null
}

export interface UploadSuccess {
  id: string
  doc_type: string
  confidence: number | null
  period: number | null
  entity_name: string | null
  page_count: number
}

export interface UploadDuplicate {
  duplicate: true
  sha256: string
}

export type UploadResult = UploadSuccess | UploadDuplicate

export function isUploadDuplicate(result: UploadResult): result is UploadDuplicate {
  return (result as UploadDuplicate).duplicate === true
}

export interface ProcessResult {
  deal_id: string
  severity_counts: SeverityCounts
  documents: number
  stage: string
}

export interface ReportLocked {
  locked: true
  severity_counts: SeverityCounts
  reason: string
}

export interface ReportUnlocked {
  locked: false
  report: DealProofReport
  watermark: string | null
}

export type ReportResponse = ReportLocked | ReportUnlocked

export interface CheckoutResult {
  checkout_url: string
  stub: boolean
  amount: string
}

export interface WebhookResult {
  received: boolean
  dev?: boolean
}

export interface PublishResult {
  published: boolean
  report_id: string
}

export interface ReclassifyResult {
  id: string
  doc_type: string
}
