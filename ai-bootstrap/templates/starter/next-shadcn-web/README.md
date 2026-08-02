# {{PROJECT_NAME}} Web — Next.js 15 + App Router + Tailwind v4 + shadcn/ui

> DEMO 视觉基线：shadcn/ui v3 官方安装范式（v3.shadcn.com/docs/installation/next）+ Tailwind v4 CSS 变量主题 + mock-first 数据，开箱即 DEMO。
> 官方范式来源：<https://v3.shadcn.com/docs/installation/next> · 组件源码：<https://ui.shadcn.com/docs/components/button>

## 目录约定（shadcn/ui v3 + Next.js App Router 官方）

- `app/layout.tsx` + `app/globals.css` — Next.js App Router 官方入口与 **shadcn 主题唯一来源**：`@import "tailwindcss"` 起步 + `:root`/`.dark` CSS 变量（`--primary` / `--radius` 等）+ `@theme inline` 把变量注册为 Tailwind 颜色令牌。
- `app/(app)/` — 路由组：应用外壳（侧边栏 + 顶栏）包裹 `dashboard` / `jobs`；`app/login/` 独立于外壳。
- `components.json` — shadcn init 官方产物（style= new-york、`rsc: true`、`css: app/globals.css`、别名 `@/components/ui`）。
- `lib/utils.ts` — shadcn 官方 `cn()`（clsx + tailwind-merge）。
- `components/ui/` — **shadcn 组件源码拷贝**（button / card / input / badge / table / dialog），由 `pnpm dlx shadcn@latest add <component>` 生成，后续新增组件同样用 `shadcn add`；交互组件（dialog 等）带 `'use client'`。
- `postcss.config.mjs` — Tailwind v4 官方 PostCSS 插件 `@tailwindcss/postcss`（create-next-app 默认）。
- `tsconfig.json` — `@/*` 路径别名指向项目根（`./*`），与 components.json aliases 一致。

## 运行

```bash
pnpm install
pnpm dev        # http://localhost:3000
```

## Mock-first 页面（登录 → 工作台 → 岗位 CRUD）

- `/login` — 演示账号直接登录（`hooks/useAuth.ts` zustand store，联调时换 API adapter）
- `/dashboard` — 工作台统计卡片 + 岗位概览表
- `/jobs` — 岗位 CRUD（shadcn Dialog + Table，数据来自 `hooks/useJobs.ts` mock port）

## 设计令牌

主题色**只改 `app/globals.css` 的 CSS 变量**（`--primary` / `--radius` 等），页面只用 `bg-primary` / `text-muted` 等语义类名，不散落 hex。
