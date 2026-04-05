/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Map to CSS variables for theming
        'bg-primary': 'var(--bg-primary)',
        'bg-secondary': 'var(--bg-secondary)',
        'bg-tertiary': 'var(--bg-tertiary)',
        'bg-hover': 'var(--bg-hover)',
        'border-subtle': 'var(--border-subtle)',
        'text-main': 'var(--text-main)',
        'text-muted': 'var(--text-muted)',
        'primary': 'var(--color-primary)',
        'primary-hover': 'var(--color-primary-hover)',
        'primary-subtle': 'var(--color-primary-subtle)',
        'success': 'var(--color-success)',
        'success-subtle': 'var(--color-success-subtle)',
        'danger': 'var(--color-danger)',
        'danger-subtle': 'var(--color-danger-subtle)',
        'warning': 'var(--color-warning)',
        'warning-subtle': 'var(--color-warning-subtle)',
        'info': 'var(--color-info)',
        'purple': 'var(--color-purple)',
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Cascadia Code', 'monospace'],
      },
      spacing: {
        'space-xs': 'var(--space-xs)',
        'space-sm': 'var(--space-sm)',
        'space-md': 'var(--space-md)',
        'space-lg': 'var(--space-lg)',
        'space-xl': 'var(--space-xl)',
        'space-2xl': 'var(--space-2xl)',
      },
      fontSize: {
        'text-xs': ['var(--font-size-xs)', { lineHeight: 'var(--line-height-base)' }],
        'text-sm': ['var(--font-size-sm)', { lineHeight: 'var(--line-height-base)' }],
        'text-base': ['var(--font-size-base)', { lineHeight: 'var(--line-height-base)' }],
        'text-lg': ['var(--font-size-lg)', { lineHeight: 'var(--line-height-tight)' }],
        'text-xl': ['var(--font-size-xl)', { lineHeight: 'var(--line-height-tight)' }],
        'text-2xl': ['var(--font-size-2xl)', { lineHeight: 'var(--line-height-tight)' }],
        'text-3xl': ['var(--font-size-3xl)', { lineHeight: 'var(--line-height-tight)' }],
      },
      borderRadius: {
        'radius-sm': 'var(--radius-sm)',
        'radius-md': 'var(--radius-md)',
        'radius-lg': 'var(--radius-lg)',
        'radius-xl': 'var(--radius-xl)',
      },
      animation: {
        'ping-slow': 'ping 2s cubic-bezier(0, 0, 0.2, 1) infinite',
        'pulse-soft': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      boxShadow: {
        'theme': 'var(--shadow-soft)',
        'glow': 'var(--shadow-glow)',
        'inset': 'var(--shadow-inset)',
      },
      backgroundImage: {
        'gradient-card': 'var(--gradient-card)',
        'gradient-header': 'var(--gradient-header)',
      },
      transitionDuration: {
        'transition-fast': '150ms',
        'transition-base': '200ms',
        'transition-slow': '300ms',
      },
    },
  },
  plugins: [],
}
