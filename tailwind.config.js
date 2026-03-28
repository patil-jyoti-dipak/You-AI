/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        bg: {
          primary: '#06090F',
          secondary: '#0C1018',
          card: '#111827',
          glass: 'rgba(255,255,255,0.04)',
        },
        accent: {
          cyan: '#00E5FF',
          orange: '#FF6B35',
          purple: '#A855F7',
          glow: 'rgba(0,229,255,0.15)',
        },
        text: {
          primary: '#E8EDF5',
          secondary: '#8892A4',
          muted: '#4A5568',
        },
      },
      fontFamily: {
        display: ['"Bebas Neue"', 'cursive'],
        body: ['"Outfit"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
        'scan': 'scan 3s linear infinite',
        'glow-pulse': 'glowPulse 2s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-12px)' },
        },
        scan: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100vh)' },
        },
        glowPulse: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(0,229,255,0.3)' },
          '50%': { boxShadow: '0 0 40px rgba(0,229,255,0.6), 0 0 80px rgba(0,229,255,0.2)' },
        },
      },
      backgroundImage: {
        'grid-pattern': `
          linear-gradient(rgba(0,229,255,0.03) 1px, transparent 1px),
          linear-gradient(90deg, rgba(0,229,255,0.03) 1px, transparent 1px)
        `,
        'hero-gradient': 'radial-gradient(ellipse 80% 60% at 50% -20%, rgba(0,229,255,0.15), transparent)',
      },
      backgroundSize: {
        'grid': '40px 40px',
      },
    },
  },
  plugins: [],
}
