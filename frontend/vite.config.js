import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path' // Import the 'path' module

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // Configure the build output directory
  build: {
    // Output directory relative to the frontend/ directory
    // We want it to go up one level (to the project root)
    // then into src/dependency_cache_visualizer/visualizer/frontend_build/
    outDir: path.resolve(__dirname, '../src/dependency_cache_visualizer/visualizer/frontend_build'),
    // Empty the output directory before building
    emptyOutDir: true,
    // Explicitly define the entry point for the build
    rollupOptions: {
      input: 'index.html'
    },
    // Optional: Configure asset file names if needed (defaults are usually fine)
    // assetsDir: 'assets',
    // rollupOptions: {
    //   output: {
    //     entryFileNames: `assets/[name]-[hash].js`,
    //     chunkFileNames: `assets/[name]-[hash].js`,
    //     assetFileNames: `assets/[name]-[hash].[ext]`
    //   }
    // }
  },
  // Optional: Configure the development server if needed
  server: {
    port: 5173, // Default Vite port
    // Proxy API requests to the Python backend during development
    proxy: {
      '/api': { // Match the prefix used in the Python backend routes
        target: 'http://127.0.0.1:8001', // Your Python backend address
        changeOrigin: true,
        // secure: false, // Uncomment if backend uses self-signed SSL cert
        // rewrite: (path) => path.replace(/^\/api/, '/api') // Ensure prefix is kept if needed
      }
    }
  }
})