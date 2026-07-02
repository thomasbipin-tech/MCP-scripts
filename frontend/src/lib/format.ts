const currencyFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 0,
})

export function formatMoney(value: string | number | undefined | null): string {
  if (value === undefined || value === null || value === '') return '—'
  const n = Number(value)
  if (Number.isNaN(n)) return '—'
  return currencyFormatter.format(n)
}

export function formatPct(value: string | number | undefined | null, digits = 1): string {
  if (value === undefined || value === null || value === '') return '—'
  const n = Number(value)
  if (Number.isNaN(n)) return '—'
  return `${n.toFixed(digits)}%`
}

export function formatMultiple(value: string | number | undefined | null): string {
  if (value === undefined || value === null || value === '') return '—'
  const n = Number(value)
  if (Number.isNaN(n)) return '—'
  return `${n.toFixed(2)}x`
}

export function formatNumber(value: string | number | undefined | null): string {
  if (value === undefined || value === null || value === '') return '—'
  const n = Number(value)
  if (Number.isNaN(n)) return String(value)
  return new Intl.NumberFormat('en-US').format(n)
}
