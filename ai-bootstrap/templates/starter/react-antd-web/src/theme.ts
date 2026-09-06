// @agent: codex
// Ant Design v6 Design Token 入口：ConfigProvider theme={{ token, algorithm }}
// 语义色与 design-system/{{PROJECT_SLUG}}/TOKENS.md 一致（enterprise-console preset）；
// 不要散落 hex 或直接改 node_modules 样式；需要暗色时切换 theme.darkAlgorithm。
import { theme } from 'antd'
import type { ThemeConfig } from 'antd'

export const antdTheme: ThemeConfig = {
  algorithm: theme.defaultAlgorithm,
  token: {
    colorPrimary: '#1677ff',
    colorInfo: '#1677ff',
    colorSuccess: '#15803d',
    colorWarning: '#b45309',
    colorError: '#b42318',
    colorTextBase: '#172033',
    colorBgLayout: '#f6f8fc',
    borderRadius: 8,
    fontSize: 14,
  },
  components: {
    Button: { controlHeight: 36 },
    Table: { headerBg: '#f2f5fa' },
  },
}
