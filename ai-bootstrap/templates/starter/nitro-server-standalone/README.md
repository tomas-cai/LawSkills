# app-web-server — Nitro API（standalone）

> Nitro 2 standalone（Node 运行时），路由位于**根级** `routes/` 与 `routes/api/`。
> Nitro ≥ 2.13 不再自动扫描 `server/` 目录，这是常见 404 根因，勿改回 `server/` 结构。

## 已验证版本

- nitropack ^2.13.x（Node 20+ / 22+ 均验证通过）
- 构建产物中路由位于 `.output/server/chunks/routes/`

## 冒烟检查

```bash
pnpm --filter @{{PROJECT_SLUG}}/web-server build
NITRO_HOST=127.0.0.1 NITRO_PORT=3100 node .output/server/index.mjs
curl http://127.0.0.1:3100/health
# {"ok":true,...}
```
