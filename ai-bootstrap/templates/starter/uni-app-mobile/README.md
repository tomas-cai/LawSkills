# {{PROJECT_NAME}} Mobile — uni-app + Vant 4 移动端（H5 优先）

> DEMO 视觉基线：Vant 4 官方引入范式 + `--van-*` 设计令牌 + mock-first 数据，开箱即 DEMO。
> 官方范式来源：<https://vant-ui.github.io/vant/#/zh-CN/quickstart> · 官方示例仓库：<https://github.com/vant-ui/vant-demo>

## 目录约定（uni-app 官方）

- `src/App.vue` — 应用生命周期 + 全局样式（`--van-*` CSS 变量在 `:root` 覆盖，H5）。
- `src/uni.scss` — uni-app 官方全局 SCSS 变量入口（编译期注入每个 `style lang="scss"` 块）。
- `src/pages.json` / `src/manifest.json` / `src/main.ts` — uni-app Vue3 + Vite 官方约定。
- `src/pages/` — 页面：`index`（工作台）/ `login`（登录）/ `jobs`（岗位列表）。
- `src/composables/` — mock-first port（页面 → composable → Mock adapter，联调替换 API adapter）。

## Vant 4 官方范式（本 DEMO 已落地）

1. **常规用法（官方推荐）**：`src/main.ts` 中 `import 'vant/lib/index.css'` 全量样式 + `app.use(Button)` 按需注册组件（Tree Shaking 默认可用）。
2. 体积极致时改用按需：`unplugin-vue-components` + `@vant/auto-import-resolver`（`VantResolver`），此时**不再**引入 `vant/lib/index.css`。
3. **反模式（不要做）**：Vant 4 起已移除 `babel-plugin-import`；禁止全量 CSS 与 VantResolver 混用（组件重复注册/样式错乱）。
4. **主题定制**：700+ 个 `--van-*` CSS 变量；全局在 `App.vue` 的 `:root` 覆盖，组件级用 `<van-config-provider :theme-vars>`。
5. **函数式 API**：`showToast` / `showDialog` 等从 `vant` 直接导入。

## 运行

```bash
pnpm install
pnpm dev:mobile   # H5: http://127.0.0.1:5173
```

> 版本说明：`@dcloudio/*` 与 `vant` 以官方最新为准，可用 `npx @dcloudio/uvm@latest` 同步 uni-app 依赖版本。
> 微信小程序端建议另用 `vant-weapp`（与 H5 的 Vant 4 是不同的包）。
