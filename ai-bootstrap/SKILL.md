---
name: ai-bootstrap
version: "1.13.1"
description: >
  AI Native Engineering Bootstrap System.
  为 AI 建立长期、统一、可治理的软件工程上下文。
  当用户需要初始化新项目、为现有项目注入 AI 治理体系、选择技术栈组合 Blueprint、
  生成治理文件（AGENTS.md / PROJECT_PROFILE.md / DESIGN.md / MEMORY.md / ADR）、
  或在 AI Agent 开始工作前统一上下文时触发。
  也可在已部分初始化的项目基础上从中段执行（如已有项目检测 → 生成治理）。
  特别适配多 Agent 协作场景（Codex / Claude Code / Cursor / Trae / Windsurf / Gemini CLI）。
  并按所选前端 UI 组件库的官方范式生成基础样式令牌、依赖与设计指导，落地为可运行的瘦 DEMO。
---

# AI Bootstrap Skill — AI Native Engineering Bootstrap System

## 核心理念

**AI Bootstrap 不是项目脚手架，而是 AI 的工程上下文注入系统。**

传统 Scaffold 生成的是代码模板，Bootstrap 生成的是 AI 认知地图。每次 Bootstrap 都是一次"AI 与项目的第一次握手"——为 AI 建立项目全貌的认知基础。

核心原则：
- **Context Before Code**: 生成任何代码前，先建立完整的工程上下文
- **Detection Before Questions**: 能自动检测的，绝不询问用户
- **Governance Over Scaffolding**: 治理体系优于代码模板
- **Multi-Agent Native**: 从第一天起支持多 Agent 协作

## 前端 Mock 与真实 API 的数据边界

当项目包含前端并预计接入后端 API 时，默认采用“轻量 port/adapter”边界：

```text
页面 / 组件 → composable 或 feature service → feature-specific port
                                      ├─ Mock adapter
                                      └─ API adapter
```

- 页面和组件只负责渲染、输入绑定和局部视图状态，不直接持有 mock 数据或 HTTP 细节。
- 先定义领域类型和用户操作接口，再用 Mock adapter 支撑交互验证，之后替换为 API adapter。
- Mock 与 API 必须实现同一套领域操作；Mock 应模拟加载、失败、ID、延迟和状态迁移，而不是只提供静态数组。
- 对一次性静态展示、没有持久化、权限、审核状态或异步流程的原型，可允许页面级 mock。
- 不因 mock/API 切换引入通用 Repository 框架、全局数据层或复杂依赖注入；接口应按业务功能保持小而具体。

## 基础功能基线（Basic Feature Baseline）

新项目 Bootstrap 默认携带一份可运行的“基础功能基线”，先保证业务演示链路完整，再按产品域增删：

- **JWT + author 鉴权（mock-first）**: 登录、注册、当前用户、退出；默认 `author` 角色；前端路由守卫；后续可切换为真实 JWT API（HttpOnly Cookie + Bearer）。
- **项目新建 / 编辑（mock-first）**: 客户项目列表、新建、编辑；Mock adapter 模拟加载、失败、ID 和状态迁移，切换 API 时保持同一 port 契约。
- 实现边界沿用上面的 Mock/API 双 adapter 规则：页面 → composable → port（Mock adapter / API adapter）。
- 若 Blueprint 声明 `starter`，`generate.py` 在全新项目生成时自动复制 `templates/starter/` 下的基线模板：单应用用 `template_dir`，多应用单仓用 `template_dirs`（复制根 + 各 `apps/<id>/` 目录），`.vue/.ts/.tsx/.js/.jsx/.json/.md/.yaml/.css` 等文本文件复制时渲染 `{{VARIABLE}}`；用 `--no-starter` 可关闭，`--starter` 可强制开启。
- 多应用单仓（`monorepo: turbo`）默认生成：pnpm workspace + Turborepo 根、Nuxt 4 前台/后台（DEMO 视觉基线：主题入口、字体插件、布局、核心组件、种子数据）、Nitro standalone API。**Nitro ≥2.13 的路由放在根级 `routes/` 与 `routes/api/`，不再自动扫描 `server/`**。
- **UI 栈官方范式（ui-stack-conformance）**: 每个前端 UI 库都按**官方 starter/quickstart 范式**初始化瘦 DEMO，并自动拦截偏离官方做法的生成品：
  - **Nuxt UI（v4 / Tailwind v4）**: `main.css` 使用 `@import "tailwindcss" theme(static)` + `@import "@nuxt/ui"` + `@theme static` 注册品牌全色阶；`app.config.ts` 声明 `ui.colors` 语义色映射；`nuxt.config.ts` 注册 `ui.theme.colors`；依赖补齐 `tailwindcss` 与 `@iconify-json/*` 图标集；只使用 `bg-primary` / `text-muted` / `border-default` 语义工具类，并标配 `app/error.vue`（UApp + UError）。**管理后台（dashboard 类页面）以官方 `nuxt-ui-templates/dashboard`（github.com/nuxt-ui-templates/dashboard）为起点**：用 `UDashboardGroup` + `UDashboardSidebar`（collapsible + resizable）+ `UDashboardPanel`/`UDashboardNavbar`/`UDashboardSearchButton` + `UNavigationMenu` 体系搭建布局，用户菜单用 `UDropdownMenu` 承载 系统设置 / 外观（明暗切换）/ 退出登录，键盘快捷键约定 `g-<首字母>` 页面跳转 + `n` 打开最近动态抽屉；共享状态用 `useState`（必须写在 composable 函数体内，模块级调用会 NUXT_E1001）而非额外引入 `@vueuse`。拦截遗留 `--mc-*` 令牌、缺失 tailwindcss、未接入 `@nuxt/ui` 等。
  - **Vant 4（移动端 / uni-app）**: 按 Vant 4 官方 quickstart 与 vant-demo 范式初始化：`src/main.ts` 全量 `import 'vant/lib/index.css'` + `app.use(Button)` 按需注册组件（官方推荐，Tree Shaking 默认可用）；体积极致时改用 `unplugin-vue-components` + `@vant/auto-import-resolver`（`VantResolver`）按需引入（此时不引入全量 css）；主题用 700+ 个 `--van-*` CSS 变量（`App.vue` `:root` 全局覆盖 + `<van-config-provider :theme-vars>` 组件级）；函数式 API `showToast` / `showDialog`。拦截 `babel-plugin-import`（Vant 4 已移除）与全量 css + VantResolver 混用。
  - **Element Plus 2.x（Vue3 PC 管理端）**: 按 Element Plus 官方 quickstart 与 theming 范式初始化（`vue-element-plus-nitro` Blueprint 内置 `apps/web` starter）：完整引入 `import ElementPlus from 'element-plus'` + `import 'element-plus/dist/index.css'` + `app.use(ElementPlus)`（快速开始，官方推荐）；体积极致时改用 `unplugin-vue-components` + `unplugin-auto-import` + `ElementPlusResolver`（来自 `unplugin-vue-components/resolvers`）按需引入（不引入全量 css）；主题用 `--el-*` CSS 变量（`src/styles/tokens.css` `:root` 全局覆盖 + 组件类名作用域覆盖）或 SCSS `@use ... with (...)`；`el-config-provider` 注入 zhCn locale；tsconfig `compilerOptions.types` 含 `element-plus/global`（Volar）。拦截 `babel-plugin-import` 与全量 css + ElementPlusResolver 混用。
  - **Ant Design v6（React 企业级）**: 按 Ant Design v6 官方快速上手与 migration-v6 范式初始化（`react-springboot` Blueprint 内置 `frontend/` starter）：`main.tsx` 用 `ConfigProvider locale={zhCN}` + `theme`（`token` + `algorithm`，Design Token 入口，v6 默认 CSS variables）+ `dayjs.locale('zh-cn')`；`import { Button } from 'antd'` 即按需（ES modules tree shaking，无 babel-plugin-import）；组件色只由 `theme.token` 驱动，`src/theme.ts` 集中定义；v6 必须移除 `@ant-design/v5-patch-for-react-19`，`@ant-design/icons` >= 6；v6 弃用 API：`bordered` → `variant`、`size='default'` → `'medium'`、children 列表 → `items`、`dropdownClassName` → `classNames.popup.root`、`iconPosition` → `iconPlacement`、Space `direction` → `orientation`。
  - **shadcn/ui（React / Next.js + Tailwind v4）**: 按 shadcn/ui v3 官方安装范式（`v3.shadcn.com/docs/installation/vite` / `.../next` + `shadcn init/add`）初始化：组件是**源码拷贝进项目**（`pnpm dlx shadcn@latest init` 生成 `components.json` + `globals.css` 主题变量 `--primary` / `--radius` + `src/lib/utils.ts` `cn()`；`pnpm dlx shadcn@latest add <component>` 拷进 `src/components/ui/`），不是 npm 依赖、不走 `babel-plugin-import` 或运行时按需插件；全局 CSS 以 `@import "tailwindcss"` 起步（Vite 用 `@tailwindcss/vite`、Next.js 用 `@tailwindcss/postcss`，配 `@/*` 路径别名；RSC 交互组件标 `'use client'`）；主题色只改 CSS 变量，页面用 `bg-primary` / `text-muted` 等语义类名，不散落 hex。（`react-fastapi` 内置 `react-shadcn-web` Vite starter（`frontend/`）；`next-fullstack` 内置 `next-shadcn-web` Next.js App Router starter（`apps/web/`）；均直接生成可运行的登录 → 工作台 → 岗位 CRUD 瘦 DEMO）
  - **Naive UI 2.x（Vue3 轻量/桌面）**: 按 Naive UI 官方快速上手与主题定制范式初始化：**不需要导入任何 CSS**（组件独立导出、tree-shaking 友好，禁止 `import 'naive-ui/dist/index.css'` 之类全量样式）；主题入口是 `<n-config-provider :theme-overrides>`（JS 对象 `GlobalThemeOverrides`；暗色用 `darkTheme`）+ `locale={zhCN}` / `date-locale={dateZhCN}`（来自 naive-ui）；按需可配 `unplugin-vue-components` + `NaiveUiResolver` + `unplugin-auto-import`；主题令牌集中在 `src/theme.ts` 导出 `themeOverrides` 对象，页面不散落 hex。（`vue-django` Blueprint 已内置 `vue-naive-web` starter：`frontend/` 直接生成可运行的登录 → 工作台 → 岗位 CRUD 瘦 DEMO）
- **官方范式优先（Official First）**: 接入任何新前端 UI 库/组件库时，**先查官方 starter / quickstart / template / theming 文档**，提取官方安装与主题入口范式 → 生成瘦 DEMO → 由 `validate.py` 的 `ui-stack-conformance` 门禁拦截反官方做法；禁止凭记忆或旧版经验初始化。已覆盖：Nuxt UI v4（管理后台按官方 dashboard 模板范式）、Vant 4、Element Plus 2.x、Ant Design v6、shadcn/ui v3、Naive UI 2.x。
- **Java/Maven 后端 starter（spring-boot-server-standalone）**: react-springboot 补齐缺失的 Spring Boot 后端工程（此前只生成前端），并新增 `vue-springboot` Blueprint（Vue3 + Element Plus + Spring Boot，国内企业级主流组合）。后端按 Spring Initializr 官方范式生成（`spring-boot-starter-parent` + `src/main/java` 官方目录 + `spring-boot-maven-plugin`），默认 H2 内存库开箱即跑、生产切换 PostgreSQL；`scripts/build_smoke.py` 支持 Maven 目标（`mvn -q -DskipTests package`），真实构建验证「生成即能跑」。**环境基线同时写入生成的 AGENTS.md / PROJECT_PROFILE.md / DESIGN.md / README：Spring Boot 3.x 用 JDK 17 最稳 + 必须支持 Maven 3.9+（`mvn -f backend/pom.xml`），指导 AI Agent 安装/切换环境时参考。**
- **环境与工具链基线（environment-baseline）**: `generate.py` 根据 Blueprint 栈把「环境与工具链基线」写入 AGENTS.md（置顶规则）、PROJECT_PROFILE.md、DESIGN.md 与 README——Spring Boot 3.x 固定 **JDK 17（最稳）+ Maven 3.9+**（pom.xml `java.version=17`，`mvn -f backend/pom.xml` 统一操作）；前端固定 Node.js 20+ LTS + pnpm。所有 Agent 在安装/切换环境、执行构建命令前必须核对（AGENTS.md 顶部）。
- **官方 DEMO 对齐清单（official-demo-checklist）**: 每个 UI 栈在 `framework_gate.py` 注册 `official_demo_url` / `official_docs_url`；生成项目的 README.md 与 `docs/00-research/design-token-spec.md` 自动附「与官方 DEMO 对齐」验收清单（官方 demo/starter 链接、官方安装范式、主题令牌入口、starter 目录、`ui-stack-conformance` 门禁），持续核对初始化是否偏离官方推荐做法。新 UI 栈入库必须先在注册表登记官方链接。
- 升级到真实 API 的路径见 `references/basic-feature-baseline.md`。

已在 `nuxt-ai-fullstack` Blueprint 中内置 `multi-app-monorepo`、`jwt + author`、`project-create-edit` 与 `demo-visual-baseline` 基线。

## 技术选型交互契约（必须遵守）

初始化新项目时，技术栈选择不是隐含推断，也不是直接套用默认 Blueprint，而是一次明确的“方案选择 → 用户确认 → 生成”交互。

### 用户未给出明确技术栈时

1. 先检测目录和运行环境；检测结果只能用于缩小范围，不能替代产品级选型。
2. 展示 `references/stack-presets.md` 中的典型方案卡片，至少包含：适用场景、完整技术组合、优势、代价、迁移触发条件。
3. 至少询问五个问题：
   - 目标端是 PC、H5、小程序还是 App？移动端是否接受独立 uni-app 应用？
   - 第一版更看重 AI 原生、Demo 速度、企业级扩展，还是模型/数据能力？
   - 是否希望前后端统一语言？
   - 预计本地部署、Vercel/Serverless，还是 Docker/云服务器？
   - 是否同时需要独立管理后台 / PC Web？如果需要，作为独立应用单独选型。
4. 给出一个推荐方案和至少一个替代方案，并明确推荐理由与主要代价。
5. 复述完整组合：每个前端应用独立列出框架及版本、UI 库、样式库、后端/API、AI SDK、数据库（本地与生产）、ORM、部署平台、包管理器。
6. 若包含前端，确认摘要必须同时展示：样式方案、图标方案、官方主题入口和设计令牌实现入口。
7. 在用户确认前，不得运行正式生成，不得创建或修改治理文件和项目代码。

### 用户已给出技术栈时

仍需把技术栈整理成完整方案并复述确认；只有用户明确使用 `--blueprint` 或明确说“按此方案直接生成”时，才可跳过再次询问。缺失的版本、生产数据库或部署信息应标为假设，并在确认摘要中指出。

### 多应用与移动端选型原则

- PC 与移动端默认是两个独立应用，不强制 PC + H5 共用一套前端；只有产品明确是轻量响应式页面时才允许合并。
- 每个应用独立选择 UI 库和样式库；共享产品级语义令牌，但不共享实现入口。
- 移动端首选 `uni-app-nitro`（uni-app + Vue3 + uni-ui + Nitro），一次开发覆盖 H5、小程序和 App；React 团队可选用 Taro + React + Ant Design Mobile。
- Blueprint 的主 `design_system` 描述主应用；多应用项目在 `stack-decision.md` 和 `design-token-spec.md` 中按应用分别声明。

### 默认优先级

- AI 相关功能：优先使用 `nuxt-ai-fullstack`（Nuxt 4 + Nitro + SQLite/Turso + Drizzle + Vercel AI SDK）。
- 企业级系统：优先使用 `react-springboot`（React + Spring Boot + PostgreSQL/MySQL）。

### 确认后的持久化要求

生成成功后，必须写入 `docs/00-research/stack-decision.md` 和 `docs/00-research/design-token-spec.md`。前者记录选择来源、Blueprint、每个应用的完整组合、理由、代价和未来迁移触发条件；后者记录共享语义令牌，以及每个应用独立的主题入口、UI 库、样式库、组件基线和首屏验收标准。已有文件不得覆盖；变更应追加新决策或进入 ADR。

## 生命周期

```
Detect ──▶ Analyze ──▶ Resolve ──▶ Generate ──▶ Verify ──▶ Complete
  │           │            │            │            │
  ▼           ▼            ▼            ▼            ▼
环境检测   项目分析    Blueprint     文件生成     自检验证
+ 工具检测  + 技术栈    解析          + 治理文件   + 完整性检查
+ 运行时    + 包管理器   + Wizard     + 上下文     + 一致性检查
            + 架构      + 确认       + 模板渲染   + 正确性检查
```

## 入口与模式选择

### 模式 1: 全新项目 Bootstrap（从零开始）

用户想要初始化一个全新项目。

```
1. 询问项目名称、描述
2. 运行 detect.py 检测环境（Node.js / Python / Go / Rust 等）
3. 根据检测结果推荐 Blueprint
4. 运行 Wizard（展示典型方案并完成技术选型确认）
5. 在技术栈确认后，先确定设计令牌基线和实现入口
6. 运行 generate.py 生成治理文件 + 设计令牌规范 + 项目骨架
7. 运行 validate.py 自检验证
```

### 模式 2: 现有项目注入治理（从检测开始）

用户已有项目代码，需要注入 AI 治理体系。

```
1. 运行 detect.py 检测已有项目
2. 自动识别技术栈、框架、架构
3. 匹配最接近的 Blueprint
4. 复述检测到的技术栈；如存在关键缺口，展示典型方案并确认补充决策
5. 对已有前端读取其主题入口；缺失时补充设计令牌基线，但不覆盖现有代码
6. 生成治理文件和设计令牌规范（不覆盖现有代码）
7. 验证兼容性
```

### 模式 3: 快速 Blueprint（从蓝图开始）

用户已有明确的技术栈选择。

```
1. 用户指定 Blueprint ID
2. 加载 Blueprint 定义
3. 询问项目名称、描述等基本信息
4. 复述 Blueprint 完整技术组合并确认
5. 确认前端主题入口和设计令牌基线
6. 生成治理文件 + 设计令牌规范 + 项目骨架
```

### 进度判定规则

```
检测目标目录 → detect.py 运行结果
  ├── 存在 docs/PROJECT_PROFILE.md → 项目已 Bootstrap → 问是否升级或重新生成
  ├── 存在 package.json / pyproject.toml / go.mod 等 → 先检测 → 问是否注入治理
  └── 空目录 → 全新项目 → 进入 Bootstrap 流程
```

## 脚本索引

| 脚本 | 用途 | 调用方式 |
|------|------|---------|
| `scripts/detect.py` | 项目环境和技术栈检测 | `python3 <skill-dir>/scripts/detect.py --dir /path/to/project` |
| `scripts/wizard.py` | 交互式 Blueprint 选择与参数收集 | `python3 <skill-dir>/scripts/wizard.py --dir /path/to/project` |
| `scripts/generate.py` | 生成治理文件 + 项目骨架 | `python3 <skill-dir>/scripts/generate.py --dir /path/to/project --blueprint <id>` |
| `scripts/validate.py` | 自检验证 | `python3 <skill-dir>/scripts/validate.py --dir /path/to/project` |
| `scripts/smoke.py` | 运行时冒烟检查（启动后验证各应用端口可访问） | `python3 <skill-dir>/scripts/smoke.py --dir /path/to/project` |
| `scripts/build_smoke.py` | 构建期冒烟（真实 `pnpm install` + 构建，验证 starter「生成即能跑」；`--plan` 只打印计划） | `python3 <skill-dir>/scripts/build_smoke.py --dir /path/to/project` |

设计令牌规范由 `generate.py` 持久化为 `docs/00-research/design-token-spec.md`；通用规则和技术栈映射见 `references/design-token-guide.md`。

### detect.py 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--dir` | 是 | 目标项目目录 |
| `--json` | 否 | JSON 格式输出（默认人类可读） |
| `--deep` | 否 | 深度检测（分析文件内容） |

### generate.py 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--dir` | 是 | 目标项目目录 |
| `--name` | 否 | 项目名称（默认使用目录名） |
| `--blueprint` | 是 | Blueprint ID（如 next-fullstack） |
| `--description` | 否 | 项目描述 |
| `--agents` | 否 | Agent 列表（逗号分隔，默认 codex,cursor） |
| `--platform` | 否 | 主 AI 平台（codex / claude-code / cursor / trae / windsurf / gemini） |
| `--dry-run` | 否 | 预览模式，只打印文件列表不写入 |
| `--force` | 否 | 明确允许覆盖已有治理文件，默认保护已有文件 |

### validate.py 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--dir` | 是 | 目标项目目录 |
| `--fix` | 否 | 自动修复可修复的问题 |
| `--json` | 否 | JSON 格式输出 |

## 模板文件体系

所有模板在 `templates/` 目录下，使用 `{{VARIABLE}}` 占位符替换：

| 模板 | 用途 | 场景 |
|------|------|------|
| `templates/governance/AGENTS.md` | Agent 角色定义和权限 | 所有项目 |
| `templates/governance/PROJECT_PROFILE.md` | 项目 DNA（唯一事实来源） | 所有项目 |
| `templates/governance/DESIGN.md` | 设计文档 | 所有项目 |
| `templates/governance/MEMORY.md` | AI 记忆文件 | 所有项目 |
| `templates/governance/ADR-INDEX.md` | ADR 目录索引 | 所有项目 |
| `templates/governance/ADR-TEMPLATE.md` | ADR 模板 | 所有项目 |
| `templates/project/README.md` | 项目 README | 全新项目 |
| `templates/project/.gitignore` | Git 忽略规则 | 全新项目 |
| `templates/starter/nuxt-basic-auth/` | 单前端基础功能基线（mock-first JWT/author 鉴权 + 项目新建/编辑） | 全新 Nuxt 单应用 |
| `templates/starter/nuxt-monorepo-root/` | 多应用单仓根（pnpm workspace + Turborepo + tsconfig.base） | nuxt-ai-fullstack 根 |
| `templates/starter/nuxt-app-hr/` | HR 前台 DEMO 视觉基线（主题/布局/组件/种子岗位；字体可选，默认跳过） | nuxt-ai-fullstack 的 app-web-hr |
| `templates/starter/nuxt-app-platform/` | 运营后台 DEMO 视觉基线（侧边栏 + 指标卡 + 动态列表；字体可选，默认跳过） | nuxt-ai-fullstack 的 app-web-platform |
| `templates/starter/nitro-server-standalone/` | Nitro standalone API（根级 routes/、健康检查、品牌欢迎页） | nuxt-ai-fullstack 的 app-web-server |
| `templates/blueprints/` | Blueprint 定义文件 | 按需加载 |
| `templates/prompt/bootstrap-complete.md` | Bootstrap 完成提示 | 流程完成 |

## 推荐 AI 技能

- Blueprint 可通过 `skills` 字段声明官方对口 AI Skill，例如 Nuxt UI 官方技能：`npx skills add nuxt/ui`，调用方式 `/nuxt-ui`。
- 生成器会把推荐技能写入 `AGENTS.md`、`README.md` 和 `PROJECT_PROFILE.md`，让 Agent 与人类开发者都知道如何安装和调用。
- 安装命令、触发词和文档链接以技术栈官方文档为准；未提供官方 Skill 的 Blueprint 不声明该字段。

## Blueprint 定义

Blueprint 定义在 `templates/blueprints/` 目录下，每个 Blueprint 一个文件：

### 已有 Blueprint

- `next-fullstack.yaml` — Next.js + NestJS + PostgreSQL + DDD 架构
- `react-fastapi.yaml` — React + FastAPI + PostgreSQL
- `react-springboot.yaml` — React + Spring Boot + PostgreSQL/MySQL
- `vue-django.yaml` — Vue + Django + PostgreSQL
- `go-microservice.yaml` — Go + Gin + PostgreSQL + gRPC
- `rust-axum-api.yaml` — Rust + Axum + SQLite
- `python-ml-service.yaml` — Python + FastAPI + PyTorch
- `nuxt-ai-fullstack.yaml` — Nuxt 4 + Nuxt UI + Nitro + Vercel AI SDK + SQLite/Turso + Drizzle
- `uni-app-nitro.yaml` — uni-app + Vue3 + Vant 4 + uni-ui + Nitro + SQLite/Turso + Vercel AI SDK
- `vue-element-plus-nitro.yaml` — Vue3 + Vite + Element Plus 2.x + Nitro + SQLite/Turso + Vercel AI SDK

### Blueprint 格式

```yaml
# templates/blueprints/next-fullstack.yaml
id: next-fullstack
name: Next.js Fullstack
version: 1.0.0
description: "Next.js 全栈应用"
tags: [nextjs, fullstack, web, ddd]

stack:
  frontend: { framework: next, language: typescript, ui_library: shadcn }
  backend: { framework: nest, language: typescript, orm: prisma }
  database: { primary: postgres, version: "17" }
  auth: { provider: authjs }
  deployment: { type: docker, platform: "vercel + railway" }
  package_manager: pnpm
  monorepo: turbo

architecture:
  style: ddd
  pattern: modular-monolith

layout:
  source_root: src/
  key_dirs:
    src/: "应用源码"
  conventions: "遵循对应技术栈官方目录约定"

commands:
  install: "pnpm install"
  dev: "pnpm dev"
  test: "pnpm test"
```

### starter 字段（可选）

Blueprint 可通过 `starter` 声明是否在全新项目生成时复制基础功能基线：

```yaml
starter:
  enabled: true
  mode: mock-first
  monorepo_dir: nuxt-monorepo-root
  template_dirs:
    - dir: nuxt-monorepo-root
      target: ""
    - dir: nuxt-app-hr
      target: apps/app-web-hr
  features:
    - jwt-author-auth
    - project-create-edit
```

- `enabled`: 是否默认启用。
- `mode`: `mock-first` 或 `api`。
- `template_dir`: 单应用场景：`templates/starter/` 下的子目录名（文本文件复制时同样渲染 `{{VARIABLE}}`，与 `template_dirs` 一致）。
- `template_dirs`: 多应用单仓场景：`{dir, target}` 列表，`dir` 是 `templates/starter/` 下的子目录，`target` 是复制到项目里的相对路径（如 `apps/app-web-hr`）；`.vue/.ts/.tsx/.js/.jsx/.json/.md/.yaml/.css` 等文本文件复制时渲染 `{{VARIABLE}}`（如 `{{PROJECT_NAME}}`、`{{PROJECT_SLUG}}`）。
- `monorepo_dir`: 多应用根目录模板（pnpm workspace + Turborepo）。
- `features`: 基础功能清单，用于生成说明与 manifest。
- Blueprint 还可声明 `apps:` 列表（`id/name/kind/port/starter_dir/checks`）；`generate.py` 会把它写入 manifest，`smoke.py` 据此探测各应用端口。

## 输出物（治理文件）

Bootstrap 保持根目录瘦：只保留工程入口与 Agent 路由；SDD 和开发过程文档按 Superpowers 阶段归档到 `docs/`，机器元数据放入 `.ai-bootstrap/`。

```
project/
├── AGENTS.md                         # Agent 路由层 + 权限矩阵
├── README.md                         # 项目说明（全新项目）
├── .gitignore                        # Git 忽略规则（全新项目）
├── docs/
│   ├── PROJECT_PROFILE.md            # 项目 DNA（唯一事实来源）
│   ├── DESIGN.md                     # 设计文档 + 架构约束
│   ├── ai/MEMORY.md                  # AI 记忆与协作状态
│   ├── 00-research/                  # 调研 + stack-decision.md + design-token-spec.md
│   ├── 01-requirements/              # 需求
│   ├── 02-specs/                     # 规格
│   ├── 03-plans/                     # 实施计划、current.md、backlog.md
│   ├── 04-reviews/                   # 审查记录
│   ├── 05-verification/              # 验证与验收证据
│   └── 06-decisions/
│       ├── adr/                      # 架构决策记录（ADR）
│       │   ├── INDEX.md
│       │   └── ADR-0001-initial-architecture.md
│       └── decisions/INDEX.md        # 非架构类决策日志
└── .ai-bootstrap/
    └── bootstrap-manifest.yaml       # 机器可读清单
```

`ADR` 是 Architecture Decision Record（架构决策记录）：它记录重要架构选择的背景、备选方案、最终决策和后果。只有影响系统结构、技术边界或长期演进的决策进入 ADR；一般的产品或实施取舍记录在 `docs/06-decisions/decisions/`。

## 目录结构处理原则

- 顶层治理结构（`AGENTS.md`、`docs/`、`.ai-bootstrap/`）在所有 Blueprint 间保持统一。
- 应用源码目录按 Blueprint 的 `layout` 声明，必须遵循对应技术栈的官方约定，不自行发明结构。
- `generate.py` 会把 `layout` 渲染到 `README.md`、`DESIGN.md` 和 `PROJECT_PROFILE.md`，让 Agent 直接看到该栈的目录契约。
- 新项目按官方约定生成骨架；现有项目不强制重构，`detect.py` 记录实际结构，AI 按现状工作。
- 多应用项目每个 app 独立声明 `layout`，不共用一套源码结构。
- Nitro standalone（≥2.13）路由放应用根级 `routes/` 与 `routes/api/`；`server/` 不再被自动扫描，存量项目按此迁移。
- 生成器自带“DEMO 视觉基线”概念：主题入口（app.config.ts）、全局令牌 CSS、布局与核心组件（AppLogo/AppHeader/AppSidebar/StatCard/EmptyState）随 starter 一起落地，避免页面停留在“无样式的功能基线”。
- **UI 字体默认跳过（国内网络友好）**: 使用 Google 字体打包（`vfonts` Lato/Inter、`@fontsource-variable/inter`）的 starter（naive-ui / Nuxt UI）**初始化默认不引入字体包**——依赖不装、import 不写，走系统字体栈（`-apple-system / PingFang SC / Microsoft YaHei`），避免国内下载慢或安装失败导致前端报错；需要官方字体时 `generate.py --fonts`（或 `AI_BOOTSTRAP_FONTS=1`）显式开启。antd / Element Plus / shadcn / vant starter 本就不依赖 Google 字体。

## 参考文件索引

| 文件 | 何时读 | 用途 |
|------|--------|------|
| `references/architecture-proposal.md` | 首次使用 | 架构设计蓝图（架构契约与演进约束） |
| `references/blueprint-guide.md` | 创建 Blueprint 时 | Blueprint 开发规范 |
| `references/stack-presets.md` | 新项目选型时 | 典型技术方案、取舍与迁移触发条件 |
| `references/design-token-guide.md` | 技术栈确认后、生成前 | 设计令牌层次、主题入口和组件基线 |

## 工作流（Codex 执行流程）

### 全面 Bootstrap 流程

当用户提出项目初始化需求时，按以下步骤执行：

#### Step 1: 收集基本信息

用户可能已经提供了一些信息。先收集必要信息：

- 项目目录（如果用户未指定，询问）
- 项目类型（全新 / 现有项目 / 从 Blueprint 开始）
- 是否有技术栈倾向

#### Step 2: 执行检测

```bash
python3 <skill-dir>/scripts/detect.py --dir /path/to/project
```

解读检测结果：
- 如果是空目录 → 全新项目
- 如果检测到已有项目 → 分析现有技术栈
- 环境信息（Node.js / Python / Go 等）

#### Step 3: 匹配 / 选择 Blueprint

根据检测结果匹配最佳 Blueprint：

- 检测到 `package.json` + `next` 依赖 → 推荐 next-fullstack
- 检测到 `package.json` + `react` + `pyproject.toml` + `fastapi` → 推荐 react-fastapi
- 检测到 Java + Spring Boot → 推荐 react-springboot
- 目标端包含 H5/小程序/App → 移动端推荐独立 uni-app 应用，不强制与 PC 共用前端
- 用户明确指定 → 确认后使用

对于空目录或技术栈不明确的项目，先读取 `references/stack-presets.md`，并按“技术选型交互契约”完成：

- 询问 AI 原生 / Demo / 企业 / 模型数据优先级
- 询问前后端是否统一语言
- 询问本地 / Vercel / Docker 部署目标
- 展示推荐方案、至少一个替代方案、完整技术组合、优点和代价
- 等用户确认后再确定 Blueprint

若 Blueprint 包含前端，在生成前读取 `references/design-token-guide.md`，检查 Blueprint 的 `design_system` 字段，并将其落实为设计令牌规范。不得把 Nuxt UI、Vant、Element Plus、Ant Design、shadcn、Naive UI 或其他 UI 库的默认主题直接当作产品最终视觉系统。

如用户提出自定义技术栈，先将其归并成一个临时方案摘要；不得因为用户说了某个框架就自行补齐未确认的数据库、部署或 AI SDK。

#### Step 4: 生成治理文件（核心）

```bash
python3 <skill-dir>/scripts/generate.py \
  --dir /path/to/project \
  --name "MyProject" \
  --blueprint next-fullstack \
  --description "项目描述" \
  --agents codex,cursor \
  --platform codex
```

如果 Blueprint 声明 `starter`（如 `nuxt-ai-fullstack`），生成器会自动复制基础功能基线（mock-first JWT/author 鉴权 + 项目新建/编辑）；需要跳过时使用 `--no-starter`。多应用单仓（`monorepo: turbo`）会先复制 monorepo 根模板，再按 `apps:` 声明把各应用模板复制到 `apps/<id>/`；`{{PROJECT_SLUG}}`/`{{PROJECT_NAME}}` 等变量在复制时渲染进文本文件。

如果用户指定 `--dry-run`，先预览再确认。

正式生成后，补写 `docs/00-research/stack-decision.md`，并把该文件纳入生成清单；同时生成 `docs/00-research/design-token-spec.md`。已有设计文件默认跳过，不能覆盖用户已有的设计决策。

#### Step 5: 验证

```bash
python3 <skill-dir>/scripts/validate.py --dir /path/to/project
```

解读验证报告：
- passed → 告知用户完成
- warning → 列出警告项，建议修复
- failed → 修复问题后重新验证

全新项目如果包含 starter 或可运行骨架，还必须执行类型检查、构建和冒烟测试：
1. `pnpm install` → `pnpm typecheck` → `pnpm build`；
2. 启动各应用后运行 `python3 <skill-dir>/scripts/smoke.py --dir /path/to/project`，确认每个端口返回 2xx/3xx；
3. 把每个可访问 URL 写进完成总结；拿不到可访问 URL 不算完成。

#### Step 6: 完成

向用户提供：
1. Bootstrap Summary（生成的文件清单）
2. 项目上下文摘要（技术栈、Agent 角色、架构风格）
3. 各应用可访问 URL 与冒烟结果（前台/后台/API 的端口与 HTTP 状态）
4. 下一步建议（"现在可以用 Codex 开始开发了"）

### 现有项目注入流程

如果用户已有项目代码需要注入治理：

```bash
# Step 1: 检测项目
python3 <skill-dir>/scripts/detect.py --dir /path/to/existing-project --deep

# Step 2: 根据检测结果生成治理文件
python3 <skill-dir>/scripts/generate.py \
  --dir /path/to/existing-project \
  --blueprint auto \
  --description "项目描述" \
  --dry-run

# Step 3: 确认后正式生成
python3 <skill-dir>/scripts/generate.py \
  --dir /path/to/existing-project \
  --blueprint auto

# 如需更新已有治理文件，必须显式使用 --force
python3 <skill-dir>/scripts/generate.py \
  --dir /path/to/existing-project \
  --blueprint auto \
  --force

# Step 4: 验证
python3 <skill-dir>/scripts/validate.py --dir /path/to/existing-project
```

**注意**: 对已有项目，只生成缺失的治理文件，默认不覆盖任何已有文件；如需重新生成已有治理文件，必须显式使用 `--force`。用户现有代码文件始终不由本流程覆盖。

## 验证检查

Bootstrap 完成后，确保以下内容正确：

- [ ] AGENTS.md 正确定义了所有 Agent 的角色和权限
- [ ] docs/PROJECT_PROFILE.md 包含完整的项目 DNA
- [ ] docs/DESIGN.md 包含架构设计和约束
- [ ] docs/ai/MEMORY.md 已初始化
- [ ] docs/00-research 至 docs/06-decisions 阶段目录已创建
- [ ] docs/00-research/stack-decision.md 记录了用户确认的完整技术组合
- [ ] docs/00-research/design-token-spec.md 存在，并声明前端/UI 库的主题入口和语义令牌
- [ ] 多应用项目：stack-decision.md 记录每个应用独立组合，design-token-spec.md 为每个应用声明独立 UI/样式库与主题入口
- [ ] README.md、DESIGN.md 和 PROJECT_PROFILE.md 已按 Blueprint `layout` 声明应用源码目录，且符合技术栈官方约定
- [ ] docs/06-decisions/adr/ 包含 ADR 索引和初始 ADR
- [ ] docs/03-plans/ 包含 current.md
- [ ] docs/04-reviews/ 包含 INDEX.md
- [ ] Blueprint 声明的技术栈与生成的治理文件一致
- [ ] 若 Blueprint 声明 starter，生成项目包含对应基础功能基线文件（mock-first），且 Markdown 中无未渲染模板标记
- [ ] PROJECT_PROFILE.md 和 README.md 包含 UI 库、AI SDK、生产数据库和部署平台
- [ ] 前端首屏实现消费设计令牌，不直接复制 UI 库默认主题或散落颜色值
- [ ] 对现有项目，未覆盖任何已有代码
- [ ] 对现有治理文件默认跳过，只有 `--force` 才覆盖
- [ ] dry-run 模式不产生实际写入
- [ ] 生成文件不包含未渲染模板标记
- [ ] .ai-bootstrap/bootstrap-manifest.yaml 已生成
- [ ] 全新项目含可运行骨架时，已执行类型检查、构建和冒烟测试，能给出可访问 URL
- [ ] Nitro standalone 应用使用根级 `routes/`/`routes/api/`（validate.py `nitro-route-layout`）
- [ ] Nuxt 应用具备 DEMO 视觉基线：主题入口、令牌 CSS、布局、EmptyState（validate.py `demo-visual-baseline`；字体为可选基线，默认跳过）
- [ ] 有构建产物时包含 Nitro 路由 chunk / Nuxt output（validate.py `build-artifacts`）
- [ ] 冒烟测试通过：每个应用端口返回 2xx/3xx（smoke.py）
- [ ] 完成总结给出每个应用的访问 URL 与冒烟结果
