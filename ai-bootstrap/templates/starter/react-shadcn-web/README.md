# {{PROJECT_NAME}} Frontend — React 19 + Vite + Tailwind v4 + shadcn/ui

> DEMO 视觉基线：shadcn/ui v3 官方安装范式（v3.shadcn.com/docs/installation/vite）+ Tailwind v4 CSS 变量主题 + mock-first 数据，开箱即 DEMO。
> 官方范式来源：<https://v3.shadcn.com/docs/installation/vite> · 组件源码：<https://ui.shadcn.com/docs/components/button>

## 目录约定（shadcn/ui v3 + Vite 官方）

- `index.html` + `src/main.tsx` — Vite 官方入口；React 19 + `react-dom/client`。
- `src/index.css` — **shadcn 主题唯一来源**：`@import "tailwindcss"` 起步 + `:root`/`.dark` CSS 变量（`--primary` / `--radius` 等）+ `@theme inline` 把变量注册为 Tailwind 颜色令牌。
- `components.json` — shadcn init 官方产物（style= new-york、`css: src/index.css`、别名 `@/components/ui`）。
- `src/lib/utils.ts` — shadcn 官方 `cn()`（clsx + tailwind-merge）。
- `src/components/ui/` — **shadcn 组件源码拷贝**（button / card / input / badge / table / dialog），由 `pnpm dlx shadcn@latest add <component>` 生成，后续新增组件同样用 `shadcn add`。
- `src/App.tsx` — 应用外壳（语义类名布局 + 侧边导航）；`src/views/` 为页面视图（Dashboard / Jobs / Login）。
- `src/hooks/` — mock-first port（页面 → hook → Mock adapter，联调替换 API adapter）。
- `vite.config.ts` + `tsconfig.json` — `@tailwindcss/vite` 插件 + `@/*` 路径别名（shadcn add 产物依赖 `@/lib/utils`）。

## shadcn/ui v3 官方范式（本 DEMO 已落地）

1. **源码拷贝，不是 npm 依赖**：组件由 `pnpm dlx shadcn@latest add <component>` 拷进 `src/components/ui/`；不要用 `babel-plugin-import` 或运行时按需插件。
2. **Tailwind v4（无 tailwind.config）**：全局 CSS 以 `@import "tailwindcss"` 起步，Vite 插件 `@tailwindcss/vite`；`@theme inline` 把 CSS 变量注册为 `bg-primary` / `text-muted` 等语义类名。
3. **主题只改 CSS 变量**：`--primary` / `--radius` 等定义在 `src/index.css`；页面不散落 hex 直接覆盖组件默认色。
4. **新增组件**：`pnpm dlx shadcn@latest add card dialog input ...`，组件会自动拷入 `src/components/ui/` 并保持 `@/*` 别名可用。

## 运行

```bash
pnpm --dir frontend install
pnpm --dir frontend dev   # http://127.0.0.1:5173
```

> 版本说明：`tailwindcss` / `@tailwindcss/vite` / `react` 以官方最新稳定版为准；升级前核对 shadcn v3 官方安装文档。
