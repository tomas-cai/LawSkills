// uni-app Vue3 + Vite 官方入口：@dcloudio/vite-plugin-uni
// Vant 4 采用官方「常规用法」：组件在 src/main.ts 用 app.use() 注册、样式全量引入 vant/lib/index.css，
// 无需在 vite.config 额外配置；体积极致时再切换到 unplugin-vue-components + @vant/auto-import-resolver。
import { defineConfig } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'

export default defineConfig({
  plugins: [uni()],
})
