import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/query': 'http://127.0.0.1:8000',
      '/compatibility-check': 'http://127.0.0.1:8000',
      '/feedback': 'http://127.0.0.1:8000',
      '/suggestion': 'http://127.0.0.1:8000',
      '/report': 'http://127.0.0.1:8000',
      '/audit': 'http://127.0.0.1:8000',
      '/health': 'http://127.0.0.1:8000',
      '/static': 'http://127.0.0.1:8000',
      '/samples': 'http://127.0.0.1:8000'
    }
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true
  }
});
