/** Shared dark chart palette; keep it aligned with the UI's semantic tokens. */
export const CHART = {
  grid: 'rgb(var(--rp-chart-grid))',
  axis: 'rgb(var(--rp-muted))',
  primary: 'rgb(var(--rp-primary))',
  primarySoft: 'rgb(var(--rp-primary-hover))',
  success: 'rgb(var(--rp-success))',
  warning: 'rgb(var(--rp-warning))',
  coral: 'rgb(var(--rp-coral))',
  info: 'rgb(var(--rp-info))',
  tick: { fontSize: 12, fill: 'rgb(var(--rp-muted))', fontFamily: 'Inter Variable, Inter, sans-serif' },
  tooltip: {
    contentStyle: {
      backgroundColor: 'rgb(var(--rp-surface))',
      color: 'rgb(var(--rp-text))',
      borderRadius: 12,
      border: '1px solid rgb(var(--rp-primary-soft))',
      boxShadow: '0 12px 32px rgb(0 0 0 / .4)',
      fontSize: 13,
    },
    labelStyle: { color: 'rgb(var(--rp-navy))' },
    cursor: { fill: 'rgb(var(--rp-primary) / .08)' },
  },
} as const;
