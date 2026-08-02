// Vue 3 + Vite 官方入口：@vitejs/plugin-vue
// Element Plus 采用官方「完整引入」：src/main.ts 引入 element-plus/dist/index.css + app.use(ElementPlus)，
// 无需在 vite.config 额外配置；体积极致时再切换 unplugin-vue-components + ElementPlusResolver 按需方案。
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
})
