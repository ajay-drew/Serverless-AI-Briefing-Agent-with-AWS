/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        surface: {
          DEFAULT: '#ffffff',
          subtle: '#fafaf9',
          muted: '#f5f5f4',
        },
        ink: {
          primary: '#1c1917',
          secondary: '#57534e',
          tertiary: '#78716c',
          muted: '#a8a29e',
        },
        border: {
          DEFAULT: '#e7e5e4',
          strong: '#d6d3d1',
        },
        accent: {
          DEFAULT: '#44403c',
          hover: '#292524',
        },
      },
      fontFamily: {
        sans: ['var(--font-sans)', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
      },
      spacing: {
        '18': '4.5rem',
        '22': '5.5rem',
      },
    },
  },
  plugins: [],
}
