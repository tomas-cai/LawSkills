# 技术方案选择参考

Wizard 在用户没有明确技术栈时，先展示方案卡片，再进入 Blueprint 选择。方案卡片不是限制，而是帮助用户快速理解取舍。

## 典型方案

| 方案 | 适合场景 | 典型技术栈 | 优势 | 代价 | 迁移触发条件 |
|---|---|---|---|---|---|
| Nuxt AI Fullstack | AI 原生 MVP、企业工作台、内容生成 | Nuxt 4 + Nuxt UI + Nitro + Vercel AI SDK + SQLite/Turso + Drizzle | 前后端统一 TS，部署简单，AI 交互顺滑 | SQLite 不适合高并发，复杂任务需异步化 | 并发写入、报表查询或长任务明显增长时迁移到独立数据库/队列 |
| Next Fullstack | React 生态、团队协作、标准 SaaS | Next.js + NestJS + PostgreSQL + Prisma + Auth.js | 生态成熟，团队招聘和扩展方便 | 前后端边界更重，初期配置成本较高 | 需要更强组织边界、多人并行和复杂领域模块时拆分服务 |
| React + FastAPI | Python AI、数据处理、模型服务 | React + FastAPI + PostgreSQL | Python AI 生态强，适合算法服务 | 前后端两套语言和部署链路 | 前端交互与业务逻辑成为主要瓶颈时补充 BFF 或统一类型契约 |
| React + Spring Boot | 企业级系统、团队协作、合规与长期维护 | React + Vite + Ant Design + Spring Boot + PostgreSQL/MySQL（运行时：**JDK 17 + Maven 3.9+**，Spring Boot 3.x 最稳组合） | Java 企业生态成熟，团队招聘和维护成本可控 | 初期配置比轻量后端重，迭代节奏偏稳 | 需要高并发云原生弹性或快速 AI 原型时评估 Go/Nuxt AI 方案 |
| Vue + Django | 内容管理、企业后台、Python 业务系统 | Vue/Nuxt + Django + PostgreSQL | Django 管理后台和 ORM 成熟 | TS 前后端统一性较弱 | 需要复用 Python 模型或 Django Admin 的复杂运营能力时保留该方案 |
| Go Microservice | 高吞吐 API、基础设施、服务拆分 | Go + Gin + PostgreSQL + gRPC | 性能和部署稳定 | 不适合快速构建复杂 AI 交互原型 | QPS、延迟或资源成本成为核心约束时采用 |
| Python ML Service | 模型实验、推理服务、数据管线 | FastAPI + PyTorch + SQLite/PostgreSQL | 适合模型和评测优先的项目 | 不适合直接承载完整产品前端 | 模型服务需要独立扩缩容、GPU 调度或实验追踪时采用 |
| UniApp + Nitro | 移动端 H5/小程序/App 多端产品 | uni-app + Vue3 + uni-ui + Nitro + Drizzle + SQLite/Turso + Vercel AI SDK | 一次开发多端覆盖，移动端首选，前后端统一 TS | 深度原生能力仍需条件编译或原生模块 | 原生 SDK、独立热更新或高性能图形成为瓶颈时评估原生 |

## 默认优先级

- **AI 相关功能**：优先 `nuxt-ai-fullstack`（Nuxt 4 + Nitro + SQLite/Turso + Drizzle + Vercel AI SDK）。
- **企业级系统**：优先 `react-springboot`（React + Spring Boot + PostgreSQL/MySQL）。
- **移动端**：优先 `uni-app-nitro`（uni-app + Vue3 + uni-ui + Nitro + SQLite/Turso + Vercel AI SDK）。

## 前端阵营首选组件库

同一项目中 PC 与移动端默认是两个独立应用，各自选择 UI 库和样式库；除非产品明确只是一个轻量响应式页面，否则不强制 PC + H5 共用一套前端。

| 阵营 | 首选组合 | 备选 | 说明 |
|---|---|---|---|
| PC Web / Vue | Nuxt 4 + Nuxt UI | Element Plus、Naive UI、PrimeVue、Ant Design Vue | Nuxt UI 留给 Nuxt 栈；Vite SPA 建议 Element Plus 或 Naive UI |
| PC Web / React | Next.js + shadcn/ui 或 Ant Design | Mantine、Arco Design、MUI | shadcn 是 Radix + Tailwind 组件模式，适合自定义设计系统 |
| PC Web / Svelte | SvelteKit + shadcn-svelte | Skeleton、Bits UI、Melt UI | 生态比 Vue/React 小，但已有成熟选择 |
| PC Web / Solid | SolidJS + Solid UI | Kobalte、SUID、Hope UI | 适合轻量、高性能和细粒度响应 |
| 移动端 H5/小程序/App | uni-app + Vue3 + uni-ui（默认搭配 `uni-app-nitro` Blueprint） | Wot Design Uni、uview-plus、NutUI | 一次开发多端覆盖，作为移动端项目首选 |
| 移动端 React | Taro + React + Ant Design Mobile | React Vant、NutUI React | 适合 React 团队的小程序/多端项目 |

### 多应用声明原则

- PC 应用与移动端应用是独立应用，不共用同一套 UI 库和样式库。
- 产品级语义令牌可以共享，但每个应用的主题入口、样式引擎、组件基线和首屏验收标准必须独立声明。
- 移动端默认推荐 uni-app：一次开发覆盖 H5、微信小程序和 App；后端按需与 Nuxt/Nitro、FastAPI、Django、Go 等现有 Blueprint 组合。
- 应用源码目录遵循对应技术栈官方约定，不同 Blueprint 使用各自 `layout`，不统一成一套 `src/` 结构。

### 目录结构官方约定

| 技术栈 | 官方源码根与核心目录 |
|---|---|
| Nuxt 4 | `app/`（pages/components/composables/layouts/middleware）+ `server/`（Nitro API） |
| Next.js | `app/`（App Router）+ `public/`；monorepo 下放 `apps/web` |
| Vite + Vue/React SPA | `src/` + `public/` |
| Spring Boot | `src/main/java` + `src/main/resources` + `src/test/java` |
| FastAPI | `app/` 应用包（api/core/models/schemas） |
| Django | `manage.py` + 项目配置包 + 业务 app |
| Go | `cmd/` + `internal/` + `pkg/` |
| Rust Axum | `src/main.rs` + 业务模块 |
| uni-app | Vue3/Vite 模板：`src/pages` + `src/components` + `src/static` + `src/pages.json`；HBuilderX 模板：`pages/` + `pages.json` |

## 选择交互

至少回答以下五个问题：

1. 目标端是什么：PC、H5、小程序还是 App？移动端是否接受独立 uni-app 应用？
2. 第一版更看重什么：快速做出可交互 Demo、企业级扩展，还是模型/数据能力？
3. 前后端是否希望统一语言？
4. 预计如何部署：本地 Demo、Vercel/Serverless，还是 Docker/云服务器？
5. 是否同时需要独立管理后台 / PC Web？如果需要，作为独立应用单独选型。

选择后必须展示：

- 推荐方案及理由
- 前端、后端、AI、数据库、部署的完整组合
- 至少一个替代方案
- 关键代价和未来迁移触发条件

## 本次实践的推荐方案

```text
Nuxt 4
Nuxt UI
Nitro server routes
Vercel AI SDK
TypeScript
本地 SQLite / Vercel Turso-libSQL
Drizzle ORM
Vercel
```

适合“先做出第一版工作台，再逐步增加课纲、PPT 和 AI 生成能力”的项目节奏。
