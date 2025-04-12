/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html", // Include the main HTML file
    "./src/**/*.{js,ts,jsx,tsx}", // Include all JS/TS/JSX/TSX files in the src directory
  ],
  theme: {
    extend: {
      // Add custom theme extensions here (colors, fonts, spacing, etc.)
      // Example:
      // colors: {
      //   'brand-blue': '#1fb6ff',
      // }
    },
  },
  plugins: [
    // Add any Tailwind plugins here (e.g., @tailwindcss/forms, @tailwindcss/typography)
  ],
}