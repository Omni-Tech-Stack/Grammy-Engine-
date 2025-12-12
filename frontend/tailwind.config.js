/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        grammy: {
          purple: '#8B5CF6',
          pink: '#EC4899',
          gold: '#F59E0B',
          dark: '#0F172A',
          darker: '#020617',
        },
      },
      backgroundImage: {
        'gradient-grammy': 'linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%)',
        'gradient-gold': 'linear-gradient(135deg, #F59E0B 0%, #FBBF24 100%)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',
      },
    },
  },
  plugins: [],
};
