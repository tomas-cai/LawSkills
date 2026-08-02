// @agent: codex
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

// ── shadcn/ui v3 官方范式（Vite + Tailwind v4）──
// 1) 全局样式入口 src/index.css：@import "tailwindcss" + CSS 变量主题（@theme inline 注册语义色）
// 2) 组件是源码拷贝进 src/components/ui/（shadcn add），不走 babel-plugin-import 或运行时按需插件
// 3) 主题只改 index.css 里的 --primary / --radius 等变量；页面用 bg-primary / text-muted 语义类名
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
