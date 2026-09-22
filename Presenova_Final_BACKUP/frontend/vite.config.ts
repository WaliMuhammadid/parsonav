import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const backendUrl = env.VITE_API_BASE_URL || 'http://localhost:5000';

  return {
    plugins: [react()],
    server: {
      port: 3000,
      open: true,
      watch: {
        ignored: ['**/release/**', '**/public/downloads/**'],
      },
      proxy: {
        '/api': {
          target: 'http://localhost:5000',
          changeOrigin: true,
        },
        '/socket.io': {
          target: 'http://localhost:5000',
          ws: true,
          changeOrigin: true,
        },
      },
    },
    build: {
      outDir: 'dist',
      sourcemap: false,
      // AUDIT-12: Split the monolithic vendor bundle into per-library chunks so the browser
      // can cache dependencies independently and load them in parallel. Prevents the single
      // ~2 MB vendor chunk that was failing the Vite chunk-size warning on every build.
      chunkSizeWarningLimit: 800,
      rollupOptions: {
        output: {
          manualChunks: (id: string) => {
            // Charting library (recharts + d3 dependencies)
            if (id.includes('node_modules/recharts') || id.includes('node_modules/d3') || id.includes('node_modules/victory')) {
              return 'charts';
            }
            // PDF generation
            if (id.includes('node_modules/jspdf') || id.includes('node_modules/pdfmake') || id.includes('node_modules/html2canvas')) {
              return 'pdf';
            }
            // WebSocket / real-time
            if (id.includes('node_modules/socket.io-client') || id.includes('node_modules/engine.io-client')) {
              return 'socket';
            }
            // React + all remaining node_modules → single vendor chunk (no circular dep risk)
            if (id.includes('node_modules/')) {
              return 'vendor';
            }
          },
        },
      },
    },
    define: {
      __BACKEND_URL__: JSON.stringify(backendUrl),
    },
  };
})
