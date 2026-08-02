# {{PROJECT_NAME}} Frontend — Vue 3 + Vite + Naive UI 2.x PC 管理端

> DEMO 视觉基线：Naive UI 2.x 官方快速上手 + 主题定制范式（零 CSS 导入 + `n-config-provider` 主题注入）+ mock-first 数据，开箱即 DEMO。
> 官方范式来源：<https://www.naiveui.com/zh-CN/os-theme> · 快速上手：<https://www.naiveui.com/zh-CN/light/docs/quick-start>

## 目录约定（Vue3 + Vite 官方）

- `index.html` + `src/main.ts` — Vite 官方入口；`app.use(naive)` 全量注册（体积极致时改 unplugin-vue-components + NaiveUiResolver 按需）。
- `src/theme.ts` — **Naive UI 主题令牌唯一来源**：`GlobalThemeOverrides` JS 对象，经 `n-config-provider :theme-overrides` 注入。
- `src/App.vue` — 应用外壳（`n-config-provider` 主题 + `zhCN`/`dateZhCN` locale + `n-layout` 布局 + `n-message-provider`）。
- `src/router.ts` — vue-router 官方路由；未登录跳转登录页（mock-first 鉴权）。
- `src/views/` — 页面视图：`DashboardView`（工作台）/ `JobsView`（岗位 CRUD）/ `LoginView`（登录）。
- `src/composables/` — mock-first port（页面 → composable → Mock adapter，联调替换 API adapter）。
- `src/styles/tokens.css` — 全局非 naive 语义层（naive 组件色由 theme.ts 驱动）。

## Naive UI 2.x 官方范式（本 DEMO 已落地）

1. **不需要导入任何 CSS**：组件独立导出、tree-shaking 友好；**禁止** `import 'naive-ui/dist/index.css'` 之类全量样式导入。
2. **主题入口**：`<n-config-provider :theme-overrides="themeOverrides">`（`GlobalThemeOverrides` JS 对象，集中 `src/theme.ts`；暗色用 `darkTheme`），页面不散落 hex。
3. **中文环境**：`locale={zhCN}` + `date-locale={dateZhCN}`（均来自 `naive-ui`）。
4. **按需可配**：`unplugin-vue-components` + `NaiveUiResolver` + `unplugin-auto-import`（此时 `main.ts` 不注册 `app.use(naive)`）。
5. **消息反馈**：`useMessage()` 必须在 `n-message-provider` 内调用（`App.vue` 已包裹）。
6. **官方字体（可选，默认跳过）**：`vfonts`（Lato / Inter，Google 字体打包为 npm 自托管）国内下载慢/易失败，默认**不引入**（`main.ts` 只保留说明注释，系统字体栈已足够）。需要时用 `generate.py --fonts` 重新生成，或手动 `pnpm add vfonts` 后在 `main.ts` 引入 `vfonts/Lato.css` / `vfonts/Inter.css`。

## 运行

```bash
pnpm --dir frontend install
pnpm --dir frontend dev   # http://127.0.0.1:5173
```

> 版本说明：`naive-ui` / `@vicons/ionicons5` / `vfonts` 以官方最新稳定版为准。
