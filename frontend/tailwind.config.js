/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    screens: { sm: '640px', md: '768px', lg: '1024px', xl: '1280px', '2xl': '1536px' },
    extend: {
      colors: {
        rp: {
          bg: 'var(--rp-bg)',
          surface: 'var(--rp-surface)',
          soft: 'var(--rp-surface-soft)',
          primary: 'var(--rp-primary)',
          'primary-hover': 'var(--rp-primary-hover)',
          'primary-light': 'var(--rp-primary-light)',
          'primary-soft': 'var(--rp-primary-soft)',
          navy: 'var(--rp-navy)',
          text: 'var(--rp-text)',
          muted: 'var(--rp-muted)',
          border: 'var(--rp-border)',
          coral: 'var(--rp-coral)',
          success: 'var(--rp-success)',
          warning: 'var(--rp-warning)',
          info: 'var(--rp-info)',
          grid: 'var(--rp-chart-grid)',
        },
      },
      fontFamily: {
        heading: ['"Manrope Variable"', 'Manrope', 'system-ui', 'sans-serif'],
        body: ['"Inter Variable"', 'Inter', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        display: ['clamp(2.5rem, 4vw, 4.25rem)', { lineHeight: '1.04', letterSpacing: '-0.03em' }],
        page: ['2rem', { lineHeight: '1.15', letterSpacing: '-0.02em' }],
        section: ['1.375rem', { lineHeight: '1.25' }],
        kpi: ['2rem', { lineHeight: '1.1' }],
      },
      borderRadius: { card: '20px', btn: '14px' },
      boxShadow: {
        card: '0 1px 2px rgba(23,27,80,.04), 0 8px 24px -12px rgba(113,56,245,.10)',
        lift: '0 2px 4px rgba(23,27,80,.06), 0 18px 36px -14px rgba(113,56,245,.22)',
        focus: '0 0 0 3px rgba(113,56,245,.28)',
      },
      spacing: { sidebar: '252px', 'sidebar-collapsed': '76px', topbar: '80px' },
      maxWidth: { content: '1440px' },
    },
  },
  plugins: [],
};
