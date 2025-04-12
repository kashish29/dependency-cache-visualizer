// postcss.config.js
// Configuration for PostCSS, often used with Tailwind CSS.
// Make sure you have installed postcss and autoprefixer:
// npm install -D postcss autoprefixer tailwindcss

export default {
  plugins: {
    tailwindcss: {}, // Apply Tailwind CSS transformations
    autoprefixer: {}, // Add vendor prefixes for browser compatibility
    // Add other PostCSS plugins here if needed
  },
}