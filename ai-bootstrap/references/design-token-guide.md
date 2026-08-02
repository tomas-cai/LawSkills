# Design Token Guide

本参考文件用于 Blueprint 选择完成后生成和审查 `docs/00-research/design-token-spec.md`。它把“框架能运行”与“产品有设计系统”分开处理。

## 必须记录的令牌层

- **语义颜色**：canvas、surface、surface-muted、ink、ink-muted、border、primary、accent、success、warning、danger、focus；至少覆盖 Light 和已启用的 Dark mode。
- **Typography**：display、heading、body、label、caption、data/code，包含字体、字号、行高、字重和 tracking。
- **Layout**：spacing scale、内容宽度、section rhythm、控件高度、密度和响应式断点。
- **Shape / depth**：圆角、边框、阴影、focus ring、overlay 层级。
- **Behavior**：hover、pressed、selected、disabled、loading、empty、error、reduced motion 和 transition timing。

## 技术栈映射规则

| 组合 | 首选实现入口 | 约束 |
|---|---|---|
| Nuxt + Nuxt UI | `app.config.ts` + 全局 CSS variables + Nuxt UI theme slots | 先映射 semantic tokens，再使用组件 slots/variants；核对当前 Nuxt UI 版本 API |
| Next/React + shadcn | 全局 CSS variables + Tailwind semantic mappings + `components/ui` variants | 官方范式（v3）：`shadcn init` 生成 `components.json` + `globals.css` 主题变量 + 组件源码拷贝进 `src/components/ui/`；全局 CSS 以 `@import "tailwindcss"` 起步；页面只使用 `bg-primary` 等语义类名，不散落 hex |
| React + MUI | `createTheme` + CssVarsProvider（如版本支持） | 用 palette/typography/shape/spacing 统一控件，避免局部 `sx` 覆盖基线 |
| Vue + Naive UI | `NConfigProvider` theme overrides + 全局 CSS variables | 官方范式（2.x）：不导入任何 CSS；`theme.ts` 集中导出 `GlobalThemeOverrides`，`n-config-provider :theme-overrides` 注入 + `zhCN`/`dateZhCN` locale |
| uni-app + uni-ui | `uni.scss` + CSS variables + uni-ui 组件主题 | 多端共用一个令牌来源，但各端按平台能力单独验收 |
| Vant 4 | CSS variables + 按需引入的组件主题 | 移动端优先校验触控目标、安全区和底部导航 |
| Vue + Element Plus | 全局 CSS variables（`--el-*`）+ `el-config-provider` | 组件主题覆盖必须在类名作用域的 `--el-*` 变量或 SCSS `@use ... with (...)` 中，禁止散落 hex |
| React + Ant Design v6 | `ConfigProvider` `theme`（`token` + `algorithm`，+ cssVar） | antd 组件色只由 `theme.token` 驱动；页面不直接改 antd 组件默认色 |
| Tailwind | CSS variables + Tailwind theme mapping | Tailwind 是映射层，不是设计决策来源 |

如果 Blueprint 使用了未列出的组合，先寻找该库官方 theme/config/provider 入口；不要用零散 CSS 覆盖替代主题层。

## 多应用独立实现

一个项目可以包含多个独立前端应用（PC Web、H5、小程序、App）。共享的只是产品级语义令牌方向，每个应用必须独立声明：

- UI 库、样式方案和图标库。
- 主题入口（`app.config.ts`、`ConfigProvider`、CSS variables、`uni.scss` 等）。
- 组件基线和平台特有验收标准（如移动端触控目标、小程序分包、App 安全区）。

推荐在 `docs/00-research/design-token-spec.md` 中先写共享语义层，再按应用写实现表：

```text
| 应用 | 框架 | UI 库 | 样式方案 | 主题入口 | 组件基线 |
| PC 管理端 | Next.js | Ant Design | CSS variables | src/theme.ts | button/input/table/form/... |
| 移动端 | uni-app | uni-ui | SCSS + CSS variables | uni.scss | button/input/list/tabbar/... |
```

不要把 PC 和 H5 的 UI 库、样式方案或主题入口强行合并成一个 `design_system`；一个应用一套实现，必要时再共享语义令牌。

## 生成与验收原则

1. 先依据项目描述确定一条设计方向和一个可解释的主色/强调色组合。
2. 使用语义名称，不在页面代码中散落 hex、任意灰阶或组件库默认色。
3. 先定义 Button、Input、Card、Badge、Navigation、Dialog、列表/表格以及 Empty/Error 的基线状态，再组合首页。
4. 首屏必须呈现清晰的产品任务、层级、密度和一个与业务有关的识别点；不能看起来像 UI 库 starter demo。
5. 在生成代码前核对安装版本的官方主题入口；生成的 Markdown 是持久化设计决策，不等同于自动写入每个框架的代码主题。
