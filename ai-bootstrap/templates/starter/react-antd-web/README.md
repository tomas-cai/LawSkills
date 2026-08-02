# {{PROJECT_NAME}} Frontend — React 19 + Ant Design 6 企业级 SPA

> DEMO 视觉基线：Ant Design v6 官方快速上手范式 + Design Token（`ConfigProvider theme.token`）+ mock-first 数据，开箱即 DEMO。
> 官方范式来源：<https://ant.design/docs/react/getting-started-cn> · v6 迁移指南：<https://ant.design/docs/react/migration-v6-cn>

## 目录约定（React + Vite 官方）

- `index.html` + `src/main.tsx` — Vite 官方入口；`ConfigProvider`（locale + theme token）统一注入。
- `src/theme.ts` — Ant Design v6 Design Token 唯一来源（`theme.token` + `algorithm`）。
- `src/App.tsx` — 应用外壳（Layout + Menu）；`src/views/` 为页面视图（Dashboard / Jobs / Login）。
- `src/hooks/` — mock-first port（页面 → hook → Mock adapter，联调替换 API adapter）。
- `src/styles/tokens.css` — 全局非 antd 语义层（antd 组件色由 theme.ts 驱动）。

## Ant Design v6 官方范式（本 DEMO 已落地）

1. **按需即默认**：antd 默认 ES modules tree shaking，`import { Button } from 'antd'` 即按需，无需 babel-plugin-import。
2. **中文 locale**：`ConfigProvider locale={zhCN}`（`antd/locale/zh_CN`）+ `import 'dayjs/locale/zh-cn'` + `dayjs.locale('zh-cn')`。
3. **主题**：`ConfigProvider theme={{ token, algorithm }}`（`src/theme.ts`）；v6 默认启用 CSS variables，需要时显式 `cssVar: true`。
4. **v6 依赖要求**：React >= 18；**必须移除** `@ant-design/v5-patch-for-react-19`；`@ant-design/icons` 需 >= 6.0.0。
5. **v6 弃用 API（不要用）**：`bordered` → `variant`（如 `variant="outlined"`）、`size="default"` → `"medium"`、列表 `children` → `items`、`dropdownClassName` → `classNames={{ popup: { root } }}`、Button `iconPosition` → `iconPlacement`、Space `direction` → `orientation`。
6. **消息反馈**：通过 `<App>`（antd）包裹 + `App.useApp()` 获取 `message`，与主题上下文一致。

## 运行

```bash
pnpm --dir frontend install
pnpm --dir frontend dev   # http://127.0.0.1:5173
```

> 版本说明：`antd` / `@ant-design/icons` 以官方最新稳定版为准；升级到 v7 前先核对官方迁移指南。
