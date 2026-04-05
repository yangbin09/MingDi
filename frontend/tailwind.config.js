/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // New warm gray palette
        gray: {
          950: '#0a0a0f',
          900: '#111827',
          800: '#1F2937',
          700: '#374151',
          600: '#4B5563',
          500: '#6B7280',
          400: '#9CA3AF',
          300: '#D1D5DB',
          200: '#E5E7EB',
          100: '#F3F4F6',
        },
        // Indigo primary accent
        indigo: {
          500: '#6366F1',
          600: '#4F46E5',
          400: '#818CF8',
          300: '#A5B4FC',
        },
        // Emerald success
        emerald: {
          500: '#10B981',
          600: '#059669',
          400: '#34D399',
        },
        // Rose danger
        rose: {
          500: '#F43F5E',
          600: '#E11D48',
          400: '#FB7185',
        },
        // Subtle backgrounds for cards
        surface: {
          primary: '#111827',
          secondary: '#1F2937',
          tertiary: '#374151',
        }
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Cascadia Code', 'monospace'],
      },
      animation: {
        'ping-slow': 'ping 2s cubic-bezier(0, 0, 0.2, 1) infinite',
        'pulse-soft': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glow: {
          '0%': { opacity: '0.03' },
          '100%': { opacity: '0.08' },
        }
      },
      boxShadow: {
        'soft': '0 4px 20px -2px rgba(0, 0, 0, 0.25), 0 2px 8px -2px rgba(0, 0, 0, 0.15)',
        'softer': '0 2px 10px -2px rgba(0, 0, 0, 0.2)',
        'indigo-glow': '0 0 20px -5px rgba(99, 102, 241, 0.3)',
        'emerald-glow': '0 0 15px -3px rgba(16, 185, 129, 0.3)',
        'rose-glow': '0 0 15px -3px rgba(244, 63, 94, 0.3)',
      },
      backgroundImage: {
        'gradient-subtle': 'linear-gradient(135deg, rgba(99, 102, 241, 0.03) 0%, rgba(16, 185, 129, 0.02) 100%)',
        'gradient-card': 'linear-gradient(180deg, rgba(255, 255, 255, 0.02) 0%, rgba(255, 255, 255, 0) 100%)',
      },
    },
  },
  plugins: [],
}
