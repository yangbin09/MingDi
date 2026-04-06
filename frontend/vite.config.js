import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    // 禁用缓存确保每次构建都生成新文件
    cache: false,
    rollupOptions: {
      output: {
        // 使用更明确的 chunk 文件名
        manualChunks: undefined
      }
    }
  }
})
