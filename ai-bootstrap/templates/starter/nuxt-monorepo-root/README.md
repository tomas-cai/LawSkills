# {{PROJECT_NAME}} — Monorepo

> 由 AI Bootstrap 生成的多应用单仓骨架（pnpm workspace + Turborepo）。
> 已验证版本：pnpm 10.x / Node ≥20 / Nuxt 4.x / Nitro 2.13+。

## 应用

| 应用 | 技术 | 端口 | 说明 |
|---|---|---|---|
| `apps/app-web-hr` | Nuxt 4 + Nuxt UI | 3000 | 面向用户/前台应用 |
| `apps/app-web-platform` | Nuxt 4 + Nuxt UI | 3002 | 运营/管理后台 |
| `apps/app-web-server` | Nitro 2（standalone） | 3100 | 后端 API |

## 官方目录约定（重要）

- **Nuxt 4**：应用源码放 `app/`（pages、layouts、components、composables、middleware、plugins、utils）。
- **Nitro standalone（≥2.13）**：路由必须放在**根级** `routes/` 与 `routes/api/`，不再自动扫描 `server/` 目录。
- 每个应用独立声明 layout、主题入口与部署配置。

## 常用命令

```bash
pnpm install        # 安装全部依赖
pnpm dev            # 同时启动三个应用
pnpm typecheck      # 全部类型检查
pnpm build          # 全部构建
```
