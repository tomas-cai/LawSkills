// @agent: codex
// Vue 3 + Vite 官方入口：@vitejs/plugin-vue
// Naive UI 2.x 官方范式：不需要导入任何 CSS、不需要 babel 插件、不需要 vite 按需插件；
// 组件直接 import { NButton } from 'naive-ui'（或 app.use(naive) 全量注册），tree-shaking 友好。
// 体积极致时再配 unplugin-vue-components + NaiveUiResolver + unplugin-auto-import。
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
})
