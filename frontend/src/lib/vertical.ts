// Vertical slugs accepted by POST /deals, with the labels used across the UI.
// The static demo sample embeds a `vertical_label` directly; API-produced
// deals/reports only carry the raw slug, so this is the fallback mapping.

export interface VerticalOption {
  value: string
  label: string
}

export const VERTICAL_OPTIONS: VerticalOption[] = [
  { value: 'hvac', label: 'HVAC / Home Services' },
  { value: 'ecommerce', label: 'E-commerce' },
  { value: 'professional_services', label: 'Professional Services' },
  { value: 'msp', label: 'Managed IT / MSP' },
  { value: 'restaurant', label: 'Restaurant / Food Service' },
  { value: 'dental', label: 'Dental Practice' },
]

export function verticalLabel(vertical: string | undefined | null): string {
  if (!vertical) return '—'
  const match = VERTICAL_OPTIONS.find((v) => v.value === vertical)
  if (match) return match.label
  return vertical
    .split('_')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
}
