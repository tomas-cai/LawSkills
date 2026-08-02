# {{PROJECT_NAME}} Web — Vue 3 + Element Plus 2.x PC 管理端

> DEMO 视觉基线：Element Plus 2.x 官方引入范式 + `--el-*` 设计令牌 + mock-first 数据，开箱即 DEMO。
> 官方范式来源：<https://element-plus.org/zh-CN/guide/quickstart.html> · 官方主题文档：<https://element-plus.org/zh-CN/guide/theming.html>

## 目录约定（Vue3 + Vite 官方）

- `index.html` + `src/main.ts` — Vite 官方入口；`src/App.vue` 承载应用外壳（el-container 布局 + 中文 locale）。
- `src/router.ts` — vue-router 官方路由；未登录跳转登录页（mock-first 鉴权）。
- `src/views/` — 页面视图：`DashboardView`（工作台）/ `JobsView`（岗位 CRUD）/ `LoginView`（登录）。
- `src/composables/` — mock-first port（页面 → composable → Mock adapter，联调替换 API adapter）。
- `src/styles/tokens.css` — `--el-*` 语义令牌全局覆盖（唯一颜色来源）。

## Element Plus 2.x 官方范式（本 DEMO 已落地）

1. **完整引入（快速开始，官方推荐）**：`src/main.ts` 中 `import ElementPlus from 'element-plus'` + `import 'element-plus/dist/index.css'` + `app.use(ElementPlus)`。
2. 体积极致时改用**按需**：`unplugin-vue-components` + `unplugin-auto-import` + `ElementPlusResolver`（来自 `unplugin-vue-components/resolvers`），此时**不再**引入 `element-plus/dist/index.css`。
3. **反模式（不要做）**：全量 css 与 ElementPlusResolver 混用；使用 `babel-plugin-import`（官方已改用 unplugin 方案）。
4. **Volar 类型**：`tsconfig.json` 的 `compilerOptions.types` 已加入 `element-plus/global`（全局组件类型提示）。
5. **主题定制**：`--el-*` CSS 变量（`:root` 全局覆盖或组件类名作用域覆盖）；需要编译期定制时用 SCSS `@use 'element-plus/theme-chalk/src/common/var.scss' with (...)`。
6. **中文 locale**：`<el-config-provider :locale="zhCn">` 统一注入（`element-plus/es/locale/lang/zh-cn`）。

## 运行

```bash
pnpm install
pnpm dev:web   # http://127.0.0.1:5173
```

> 版本说明：`element-plus` 与 `@element-plus/icons-vue` 以官方最新稳定版为准。
