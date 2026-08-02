// @agent: codex
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import naive from 'naive-ui'
import App from './App.vue'
import router from './router'
import './styles/tokens.css'
// Naive UI 官方推荐字体（vfonts，可选）：主题与中文排版更完整
import 'vfonts/Lato.css'
import 'vfonts/Inter.css'

// ── Naive UI 2.x 官方范式 ──
// 1) 不需要导入任何 CSS：组件独立导出、tree-shaking 友好；不要全量导入样式文件（dist 下 index.css 属反模式）
// 2) 全量注册 app.use(naive) 或按需 import { NButton } from 'naive-ui'
//    （体积极致时用 unplugin-vue-components + NaiveUiResolver + unplugin-auto-import）
// 3) 中文环境与主题：n-config-provider :locale="zhCN" :date-locale="dateZhCN" :theme-overrides（见 App.vue / theme.ts）
const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(naive)
app.mount('#app')
