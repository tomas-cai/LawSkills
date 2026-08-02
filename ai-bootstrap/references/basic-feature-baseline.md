# 基础功能基线：JWT + author 鉴权 / 项目新建编辑

## 目标

新项目 Bootstrap 后默认拥有一套可运行、可演示、可替换的基础功能，先保证“登录 → 工作台 → 新建/编辑项目”链路完整，再按产品域增删。

## 一、鉴权基线（mock-first）

- 角色：`author`（内容作者 / 培训师）
- 能力：登录、注册、当前用户、退出、路由守卫
- Mock adapter：localStorage 会话 + 演示账号 `demo@trainer.local` / `demo1234`
- API adapter（升级后）：
  - `POST /api/auth/register`
  - `POST /api/auth/login`
  - `GET /api/auth/me`
  - `POST /api/auth/logout`
- JWT 约定：HS256；HttpOnly Cookie `ta_session` + `Authorization: Bearer`；默认 7 天
- 密码：真实实现使用 scrypt 加盐哈希与恒定时间比较

## 二、项目基线（mock-first）

- 能力：列表、新建、编辑、状态（`draft` / `active` / `completed` / `archived`）
- Mock adapter：localStorage 持久化，模拟加载延迟与 ID 生成
- API adapter：`GET/POST /api/projects`、`GET/PATCH /api/projects/:id`
- 数据隔离：真实 API 按 `author_id` 校验归属，跨作者访问返回 `403`

## 三、双 adapter 契约

```text
页面 / 组件 → composable（useAuth / useProjects）→ feature port
                                        ├─ Mock adapter
                                        └─ API adapter（$fetch）
```

- 页面只负责渲染、输入绑定和局部视图状态，不直接持有 mock 数据或 HTTP 细节。
- Mock 与 API 必须实现同一套领域操作；Mock 模拟加载、失败、ID、延迟和状态迁移。
- 切换 API 时只替换 composable 内部 adapter，页面零改动。

## 四、验收标准

- 未登录访问工作台跳转 `/login`，登录后回到原目标页。
- 登录后只能看到自己的客户项目，新建后回到列表。
- 编辑可修改客户名称、标题、状态并持久化。
- 切换到真实 API 后，页面与路由守卫行为不变。

## 五、升级路径

1. 在服务端实现 JWT 签发 / 校验与 scrypt 密码哈希。
2. 增加 `users` 表与 `training_projects.author_id`，按作者隔离数据。
3. 将 `useAuth` / `useProjects` 的 mock 分支替换为 `$fetch` 调用。
4. 配置 `NUXT_JWT_SECRET`，补充数据库迁移、速率限制与审计。
