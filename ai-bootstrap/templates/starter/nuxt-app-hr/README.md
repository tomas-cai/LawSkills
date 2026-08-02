# app-web-hr — {{PROJECT_NAME}} HR 前台（Nuxt 4 + Nuxt UI）

> DEMO 视觉基线：品牌区 + 统一布局 + Nuxt UI v4 官方主题范式 + 种子数据，开箱即 DEMO。
> 已验证版本：nuxt ^4.0.0 / @nuxt/ui ^4.0.0 / tailwindcss ^4.3.0 / @nuxt/icon ^2.4.0 / vue-tsc ^3.3.9 / @fontsource-variable/inter ^5.2.0（可选，默认跳过）。

## 目录约定（Nuxt 4）

- 应用源码统一放在 `app/`：pages、layouts、components、composables、middleware、plugins、utils。
- 主题入口：`app/app.config.ts`（Nuxt UI `ui.colors` 语义色映射 + font）。
- 品牌令牌：`app/assets/css/main.css` 的 `@theme static`（`--color-brand-*` / `--color-accent-*` 全色阶），遵循 Nuxt UI v4 / Tailwind v4 官方范式。
- 语义色注册：`nuxt.config.ts` 的 `ui.theme.colors`。
- 字体加载（**可选，默认跳过**）：`@fontsource-variable/inter`（Google 字体打包）国内下载慢/易失败，默认不引入（`fonts.ts` / `main.css` 只留说明注释，走系统字体栈）；需要时用 `generate.py --fonts` 重新生成。
- 页面只使用 `bg-primary` / `text-muted` / `border-default` 等语义工具类，禁止散落 hex 与 `--mc-*` 自定义令牌。

## 冒烟检查

```bash
pnpm --filter @{{PROJECT_SLUG}}/web-hr dev
# http://127.0.0.1:3000 → /login → 演示账号一键登录 → 工作台
```
