// @agent: codex
// shadcn/ui v3（Tailwind v4 + Vite）官方接入：
// 1) 插件用 @tailwindcss/vite（Tailwind v4 官方 Vite 插件，不再需要 tailwind.config 与 postcss）
// 2) 全局 CSS 以 @import "tailwindcss" 起步（src/index.css）
// 3) @/* 路径别名：tsconfig paths + vite resolve.alias（shadcn add 生成的组件依赖 @/lib/utils）
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
