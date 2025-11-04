import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // Allow access from any IP address
    port: 5173,
    strictPort: false, // Allow fallback to different port if 5173 is busy
    open: true, // Automatically open browser
  },
});