import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '.', '');
  return {
    base: './',
    server: {
      port: 5000,
      host: '0.0.0.0',
      proxy: {
        '/chat': 'http://localhost:8000',
        '/chats': 'http://localhost:8000',
        '/monster': 'http://localhost:8000',
        '/memory': 'http://localhost:8000',
        '/user': 'http://localhost:8000',
        '/overlay': 'http://localhost:8000',
      }
    },
    plugins: [react()],
    define: {
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
      }
    }
  };
});
