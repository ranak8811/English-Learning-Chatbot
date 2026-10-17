/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        child: {
          yellow: '#FEF08A',
          orange: '#FED7AA',
          blue: '#BAE6FD',
          pink: '#FBCFE8',
          green: '#BBF7D0',
          purple: '#E9D5FF'
        }
      }
    },
  },
  plugins: [],
}
