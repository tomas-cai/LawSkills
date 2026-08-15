# {{PROJECT_NAME}} · 平台运营管理后台（app-web-platform）

基于 **Nuxt UI v4 官方 Dashboard 模板范式**（[nuxt-ui-templates/dashboard](https://github.com/nuxt-ui-templates/dashboard)）构建的运营管理后台起步基线。

## 布局体系（官方范式）

| 组件 | 职责 |
|---|---|
| `UDashboardGroup` + `UDashboardSidebar` | 侧边栏骨架：可折叠（collapsible）+ 可拖拽调宽（resizable） |
| `UDashboardSearchButton` + `UDashboardSearch` | 全局命令面板（`⌘K`） |
| `UNavigationMenu` | 侧边栏导航（vertical + tooltip + popover） |
| `UDashboardPanel` + `UDashboardNavbar` | 每个页面的内容面板与顶栏（含 `UDashboardSidebarCollapse`） |
| `UserMenu` | 用户菜单：明暗主题切换 + 系统设置 + 退出 |
| `NotificationsSlideover` | 右侧「最近动态」抽屉（`USlideover`） |

## 约定

- 页面一律使用 `UDashboardPanel`（header/body 两个 slot），不再手写 `min-h-screen` 布局。
- 键盘快捷键：`g-h` 运营概览、`g-e` 企业管理、`g-j` 岗位管理、`g-s` 系统设置、`n` 打开最近动态。
- 种子数据集中在 `app/utils/dashboard.ts`（mock-first 边界），接入真实 API 时替换数据源即可。
- 主题令牌入口：`app/app.config.ts`（语义色映射）+ `app/assets/css/main.css`（`@theme static` 品牌色阶）。
- 组件内只使用 `bg-primary` / `text-muted` / `border-default` / `bg-elevated` 等语义工具类，禁止散落 hex。

## 开发

```bash
pnpm --filter @{{PROJECT_SLUG}}/web-platform dev
```
