import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

/** Прокси на Django: одинаково для `vite` и `vite preview` (Docker). */
const djangoProxy = {
  '/api': {
    target: 'http://backend:8000',
    changeOrigin: true,
  },
  '/media': {
    target: 'http://backend:8000',
    changeOrigin: true,
  },
  '/predictImage': {
    target: 'http://backend:8000',
    changeOrigin: true,
  },
  '/uploadModel': {
    target: 'http://backend:8000',
    changeOrigin: true,
  },
  '/mlflowModels': {
    target: 'http://backend:8000',
    changeOrigin: true,
  },
};

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    host: '0.0.0.0',
    proxy: djangoProxy,
  },
  preview: {
    port: 5173,
    host: '0.0.0.0',
    proxy: djangoProxy,
  },
});
