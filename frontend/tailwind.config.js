/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Sonic Obsidian Design System - Voice AI Platform
        surface: {
          DEFAULT: '#10131a',
          dim: '#10131a',
          bright: '#363940',
          lowest: '#0b0e14',
          low: '#191c22',
          high: '#272a31',
          highest: '#32353c',
        },
        primary: {
          DEFAULT: '#afecff',
          container: '#00d9ff',
          fixed: '#aeecff',
          'fixed-dim': '#00d9ff',
        },
        cyan: {
          glow: '#00D9FF',
          50: '#f0faff',
          100: '#e0f5ff',
          200: '#b3e8ff',
          300: '#80daff',
          400: '#4dcbff',
          500: '#00d9ff',
          600: '#00acc8',
          700: '#0081a1',
          800: '#00667c',
          900: '#004d5a',
        },
        on: {
          primary: '#003641',
          'primary-container': '#005b6c',
          surface: '#e1e2eb',
          'surface-variant': '#bbc9ce',
        },
        secondary: {
          DEFAULT: '#c2c7d0',
          container: '#42474f',
        },
        tertiary: {
          DEFAULT: '#b2ecfd',
          container: '#97d0e0',
        },
        error: {
          DEFAULT: '#ffb4ab',
          container: '#93000a',
        },
        background: '#10131a',
      },
      fontFamily: {
        display: ['Inter', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
        mono: ['Space Grotesk', 'monospace'],
      },
      boxShadow: {
        'cyan-glow': '0 0 20px rgba(0, 217, 255, 0.4)',
        'cyan-glow-lg': '0 0 40px rgba(0, 217, 255, 0.6)',
        'glass': '0 4px 30px rgba(0, 0, 0, 0.3)',
      },
      backdropBlur: {
        glass: '20px',
      },
      animation: {
        'voice-bar': 'bounce 1s ease-in-out infinite',
        'pulse-slow': 'pulse 3s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 10px rgba(0, 217, 255, 0.3)' },
          '100%': { boxShadow: '0 0 25px rgba(0, 217, 255, 0.7)' },
        },
      },
      borderRadius: {
        DEFAULT: '8px',
        sm: '4px',
        md: '12px',
        lg: '16px',
        xl: '24px',
      },
      spacing: {
        'gutter': '16px',
        'page': '32px',
      },
    },
  },
  plugins: [],
}
