import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],

  // 路径别名配置
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },

  // 构建优化配置
  build: {
    // 输出目录
    outDir: 'dist',
    // 生成 sourcemap 用于生产环境调试
    sourcemap: false,
    // 代码分割策略
    rollupOptions: {
      output: {
        manualChunks: {
          // React 相关库单独打包
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          // Ant Design 单独打包
          'antd-vendor': ['antd', '@ant-design/icons'],
        },
      },
    },
    // chunk 大小警告限制
    chunkSizeWarningLimit: 1000,
  },

  // 开发服务器配置
  server: {
    port: 5173,
    // 开发环境代理配置（可选）
    proxy: {
      '/api': {
        target: process.env.VITE_API_BASE_URL || 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
