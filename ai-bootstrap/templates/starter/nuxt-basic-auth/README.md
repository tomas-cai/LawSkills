# Basic Feature Baseline — Nuxt Mock-First Starter

> 由 AI Bootstrap 生成的“基础功能基线”：mock-first 的 JWT + author 鉴权，以及项目新建/编辑。
> 全部代码先以 Mock adapter 运行，业务联调时可替换为真实 API adapter。

## 包含内容

- author 鉴权：登录、注册、当前用户、退出、路由守卫
- 客户培训项目：列表、新建、编辑（mock 持久化到 localStorage）
- 演示作者账号：demo@trainer.local / demo1234

## 使用方式

1. 先确认项目已安装 Nuxt 4 + Nuxt UI + TypeScript。
2. 启动应用后访问 /login 登录或注册。
3. 进入工作台后新建项目，再从项目卡片进入编辑页。

## Mock 与 API 边界

- 页面只调用 composable：useAuth、useProjects。
- composable 内部先走 Mock adapter，API adapter 使用同一领域操作签名。
- 切换到真实 API 时，把 useAuth / useProjects 中的 mock 分支替换为 $fetch 调用，保持页面不变。
- 真实 JWT 服务端基线说明见 `references/basic-feature-baseline.md`。

## 注意

- 这是可运行演示，不是生产认证；真实部署必须配置 JWT 密钥并补充密码策略、速率限制与审计。
