// @agent: codex
import React from 'react'
import ReactDOM from 'react-dom/client'
import { App as AntdApp, ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'
import App from './App'
import { antdTheme } from './theme'
import './styles/tokens.css'

// ── Ant Design v6 官方快速上手范式 ──
// 1) antd 默认 ES modules tree shaking：import { Button } from 'antd' 即按需，无需 babel-plugin-import
// 2) 中文 locale：ConfigProvider locale={zhCN} + dayjs.locale('zh-cn')
// 3) 主题：ConfigProvider theme={{ token, algorithm }}（Design Token 入口；v6 默认启用 CSS variables）
// 4) v6 不再需要 @ant-design/v5-patch-for-react-19（必须移除）；@ant-design/icons 需 >= 6
dayjs.locale('zh-cn')

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfigProvider locale={zhCN} theme={antdTheme}>
      <AntdApp>
        <App />
      </AntdApp>
    </ConfigProvider>
  </React.StrictMode>,
)
