/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    screens: { sm: '640px', md: '768px', lg: '1024px', xl: '1280px', '2xl': '1536px' },
    extend: {
      colors: {
        rp: {
          bg: 'rgb(var(--rp-bg) / <alpha-value>)',
          surface: 'rgb(var(--rp-surface) / <alpha-value>)',
          soft: 'rgb(var(--rp-surface-soft) / <alpha-value>)',
          'surface-soft': 'rgb(var(--rp-surface-soft) / <alpha-value>)',
          action: 'rgb(var(--rp-action) / <alpha-value>)',
          'action-hover': 'rgb(var(--rp-action-hover) / <alpha-value>)',
          overlay: 'rgb(var(--rp-overlay) / <alpha-value>)',
          magenta: 'rgb(var(--rp-magenta) / <alpha-value>)',
          primary: 'rgb(var(--rp-primary) / <alpha-value>)',
          'primary-hover': 'rgb(var(--rp-primary-hover) / <alpha-value>)',
          'primary-light': 'rgb(var(--rp-primary-light) / <alpha-value>)',
          'primary-soft': 'rgb(var(--rp-primary-soft) / <alpha-value>)',
          navy: 'rgb(var(--rp-navy) / <alpha-value>)',
          text: 'rgb(var(--rp-text) / <alpha-value>)',
          muted: 'rgb(var(--rp-muted) / <alpha-value>)',
          border: 'rgb(var(--rp-border) / <alpha-value>)',
          coral: 'rgb(var(--rp-coral) / <alpha-value>)',
          success: 'rgb(var(--rp-success) / <alpha-value>)',
          warning: 'rgb(var(--rp-warning) / <alpha-value>)',
          info: 'rgb(var(--rp-info) / <alpha-value>)',
          grid: 'rgb(var(--rp-chart-grid) / <alpha-value>)',
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
      borderRadius: { card: '20px', btn: '12px' },
      boxShadow: {
        card: 'inset 0 1px 0 rgba(216,180,255,.04), 0 8px 28px -16px rgba(0,0,0,.5)',
        lift: '0 18px 48px -12px rgba(0,0,0,.65)',
        focus: '0 0 0 3px rgba(191,137,255,.25)',
      },
      spacing: { sidebar: '252px', 'sidebar-collapsed': '76px', topbar: '80px' },
      maxWidth: { content: '1440px' },
    },
  },
  plugins: [],
};
