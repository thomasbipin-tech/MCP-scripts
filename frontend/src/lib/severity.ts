import type { Severity } from '../types/report'

export const SEVERITY_ORDER: Severity[] = ['CRITICAL', 'HIGH', 'MEDIUM', 'INFO']

export const SEVERITY_LABEL: Record<Severity, string> = {
  CRITICAL: 'Critical',
  HIGH: 'High',
  MEDIUM: 'Medium',
  INFO: 'Info',
}

// Tailwind class bundles per severity — used for chips / left borders / tiles.
export const SEVERITY_CLASSES: Record<
  Severity,
  { text: string; bg: string; border: string; chip: string; dot: string }
> = {
  CRITICAL: {
    text: 'text-signal-500',
    bg: 'bg-signal-500/10',
    border: 'border-signal-500/40',
    chip: 'bg-signal-500/10 text-signal-400 border-signal-500/30',
    dot: 'bg-signal-500',
  },
  HIGH: {
    text: 'text-amber-500',
    bg: 'bg-amber-500/10',
    border: 'border-amber-500/40',
    chip: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    dot: 'bg-amber-500',
  },
  MEDIUM: {
    text: 'text-yellow-600',
    bg: 'bg-yellow-600/10',
    border: 'border-yellow-600/40',
    chip: 'bg-yellow-600/10 text-yellow-500 border-yellow-600/30',
    dot: 'bg-yellow-600',
  },
  INFO: {
    text: 'text-blue-400',
    bg: 'bg-blue-400/10',
    border: 'border-blue-400/40',
    chip: 'bg-blue-400/10 text-blue-300 border-blue-400/30',
    dot: 'bg-blue-400',
  },
}
