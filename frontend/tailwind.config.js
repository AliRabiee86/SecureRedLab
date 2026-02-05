/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Modern Cyber Palette
        cyber: {
          black: '#020617', // Deep Space Black
          darker: '#0f172a',
          dark: '#1e293b',
          blue: '#38bdf8', // Neon Blue
          green: '#22c55e', // Security Green
          red: '#ef4444', // Alert Red
          purple: '#8b5cf6', // Logic Purple
          gold: '#eab308', // Warning Gold
          gray: '#94a3b8',
        },
        // Semantic Colors
        surface: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          800: '#1e293b',
          900: '#0f172a',
          950: '#020617',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      animation: {
        'pulse-fast': 'pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow-blue': 'glow-blue 2s ease-in-out infinite alternate',
        'glow-green': 'glow-green 2s ease-in-out infinite alternate',
        'float': 'float 6s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
      },
      keyframes: {
        'glow-blue': {
          '0%': { 'box-shadow': '0 0 5px rgba(56, 189, 248, 0.2)' },
          '100%': { 'box-shadow': '0 0 20px rgba(56, 189, 248, 0.6)' },
        },
        'glow-green': {
          '0%': { 'box-shadow': '0 0 5px rgba(34, 197, 94, 0.2)' },
          '100%': { 'box-shadow': '0 0 20px rgba(34, 197, 94, 0.6)' },
        },
        'float': {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        'shimmer': {
          '100%': { transform: 'translateX(100%)' },
        }
      },
      backgroundImage: {
        'cyber-grid': "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='40' viewBox='0 0 40 40'%3E%3Cpath d='M0 40 L40 40 L40 0 M0 0 L0 40' fill='none' stroke='rgba(56, 189, 248, 0.05)' stroke-width='1'/%3E%3C/svg%3E\")",
        'noise': "url('https://grainy-gradients.vercel.app/noise.svg')",
      }
    },
  },
  plugins: [],
}
