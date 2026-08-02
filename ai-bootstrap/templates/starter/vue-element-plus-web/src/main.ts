// @agent: codex
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './styles/tokens.css'

// ── Element Plus 2.x 官方范式 · 完整引入（快速开始，官方推荐）──
// 1) 全量引入样式 element-plus/dist/index.css
// 2) app.use(ElementPlus) 注册全部组件
// 体积极致时切换官方按需方案：unplugin-vue-components + unplugin-auto-import
// + ElementPlusResolver（来自 unplugin-vue-components/resolvers），此时不再引入全量 css。
// 反模式：不要同时配置 ElementPlusResolver 与全量 css；不要使用 babel-plugin-import。
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.mount('#app')
