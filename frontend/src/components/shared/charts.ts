/** Shared chart styling so every page's charts match. */
export const CHART = {
  grid: 'var(--rp-chart-grid)',
  axis: '#666B85',
  primary: '#7138F5',
  primarySoft: '#C9B2FB',
  success: '#16865C',
  warning: '#A96A12',
  coral: '#F36B57',
  info: '#3478D4',
  tick: { fontSize: 12, fill: '#666B85', fontFamily: 'Inter Variable, Inter, sans-serif' },
  tooltip: {
    contentStyle: { borderRadius: 14, border: '1px solid #EAE5EE', boxShadow: '0 10px 24px -12px rgba(23,27,80,.25)', fontSize: 13 },
    cursor: { fill: 'rgba(113,56,245,.06)' },
  },
} as const;
