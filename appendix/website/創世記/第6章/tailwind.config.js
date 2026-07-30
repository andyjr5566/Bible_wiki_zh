/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html','./src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        'wood-dark': '#1c130b',
        'wood-primary': '#3e2723',
        'gold-divine': '#d4af37',
        'parchment': '#fcf8f2',
        'deluge-dark': '#0a1118',
        'deluge-mid': '#1a2a3a',
        'rainbow-red': '#e74c3c',
        'rainbow-orange': '#e67e22',
        'rainbow-yellow': '#f1c40f',
        'rainbow-green': '#2ecc71',
        'rainbow-blue': '#3498db',
        'rainbow-indigo': '#9b59b6',
        'rainbow-violet': '#8e44ad'
      },
      fontFamily: {
        serif: ['"Noto Serif TC"','serif'],
        sans: ['"Noto Sans TC"','sans-serif']
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'sway': 'sway 4s ease-in-out infinite',
        'rain-fall': 'rain-fall 0.5s linear infinite',
        'fade-in': 'fade-in 1.5s ease-out'
      },
      keyframes: {
        float: { '0%,100%': { transform: 'translateY(0)' }, '50%': { transform: 'translateY(-10px)' } },
        sway: { '0%,100%': { transform: 'rotate(-1deg)' }, '50%': { transform: 'rotate(1deg)' } },
        'rain-fall': { '0%': { transform: 'translateY(-100%)' }, '100%': { transform: 'translateY(100vh)' } },
        'fade-in': { '0%': { opacity: 0 }, '100%': { opacity: 1 } }
      }
    }
  },
  plugins: []
}
