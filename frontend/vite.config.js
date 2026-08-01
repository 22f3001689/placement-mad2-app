import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': 'http://localhost:5000',
    },
  },
  build: {
    outDir: '../app/static/dist',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        // Stable filenames so the Jinja shell can reference them directly,
        // without needing to parse Vite's manifest.json.
        entryFileNames: 'index.js',
        assetFileNames: 'index.[ext]',
      },
    },
  },
})
