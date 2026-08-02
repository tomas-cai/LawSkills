import { createSSRApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

// ── Vant 4 官方范式 · 常规用法（官方推荐）──
// 1) 全量引入样式 vant/lib/index.css
// 2) 按需 app.use(Button) 注册组件（Tree Shaking 默认可用）
// 反模式：不要同时配置 @vant/auto-import-resolver 按需引入；Vant 4 起禁止 babel-plugin-import。
import 'vant/lib/index.css'
import {
  Button,
  Cell,
  CellGroup,
  ConfigProvider,
  Empty,
  Field,
  NavBar,
  Tabbar,
  TabbarItem,
} from 'vant'

export function createApp() {
  const app = createSSRApp(App)
  app.use(createPinia())
  app.use(Button)
  app.use(Cell)
  app.use(CellGroup)
  app.use(ConfigProvider)
  app.use(Empty)
  app.use(Field)
  app.use(NavBar)
  app.use(Tabbar)
  app.use(TabbarItem)
  return { app }
}
