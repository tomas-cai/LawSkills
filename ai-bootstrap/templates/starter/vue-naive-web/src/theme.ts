// @agent: codex
// Naive UI 2.x 主题令牌唯一来源：GlobalThemeOverrides JS 对象
// 语义色与 docs/00-research/design-token-spec.md 一致（structured operations desk preset）；
// 页面不散落 hex；需要暗色时切换 darkTheme（来自 naive-ui，与 themeOverrides 合并传入）。
import type { GlobalThemeOverrides } from 'naive-ui'

export const themeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#2563EB',
    primaryColorHover: '#3B82F6',
    primaryColorPressed: '#1D4ED8',
    primaryColorSuppl: '#2563EB',
    infoColor: '#2563EB',
    successColor: '#15803D',
    warningColor: '#B45309',
    errorColor: '#B42318',
    borderRadius: '8px',
    fontFamily:
      "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif",
  },
  // 组件级覆盖示例（DataTable 表头底色、Card 边框）：
  // Card: { borderColor: '#E4E9F2' },
  // DataTable: { thColor: '#F2F5FA', borderColor: '#E4E9F2' },
}
