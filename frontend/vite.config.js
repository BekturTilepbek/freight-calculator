import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    // Для hot-reload в Docker на Windows/WSL — следит за изменениями через polling
    watch: {
      usePolling: true,
    },
    // Прокси — самая важная часть. Все запросы фронта на /api/*
    // Vite перенаправит на backend-контейнер. Никаких CORS-проблем.
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
    },
  },
})