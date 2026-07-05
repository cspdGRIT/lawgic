import type { Config } from 'tailwindcss'
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        serif: ['Playfair Display', 'Georgia', 'serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
        crimson: ['Crimson Text', 'Georgia', 'serif'],
      },
      colors: {
        primary: {
          50: '#f8f8f8',
          100: '#f0f0f0',
          900: '#0a0a0a',
        },
        accent: '#1a1a2e',
        gold: '#c9a84c',
      },
    },
  },
  plugins: [],
} satisfies Config
