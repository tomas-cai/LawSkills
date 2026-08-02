# AI Bootstrap

> AI Native Engineering Bootstrap System
>
> 为 AI 建立长期、统一、可治理的软件工程上下文。
>
> 当前版本：1.10.0 ｜ 执行规范：[SKILL.md](./SKILL.md)

## 版本记录

- `1.10.0`（当前）：shadcn/ui 与 Naive UI 落地「生成即能跑 + 校验即通过」的瘦 DEMO starter：`react-fastapi` Blueprint 内置 `react-shadcn-web` starter（`frontend/`，Vite + React 19 + Tailwind v4 + `@tailwindcss/vite` + `components.json` + `src/index.css` 主题 CSS 变量 + `src/components/ui/` 源码拷贝组件（button/card/input/badge/table/dialog）+ `src/lib/utils.ts` `cn()` + `@/*` 别名 + 语义类名页面，登录 → 工作台 → 岗位 CRUD 开箱即跑）；`vue-django` Blueprint 内置 `vue-naive-web` starter（`frontend/`，Vue3 + Vite + Naive UI 2.x：零 CSS 导入 + `n-config-provider :theme-overrides` + `GlobalThemeOverrides` 集中 `theme.ts` + `zhCN`/`dateZhCN` locale + `n-*` 组件基线页面）；`ui-stack-conformance` 对 shadcn/naive 的官方范式检查升级为「生成即通过」（starter 正样零 warning），并保留反模式拦截（`babel-plugin-import`、`naive-ui/dist` 全量 CSS）。
- `1.9.0`：官方范式门禁扩展至 shadcn/ui 与 Naive UI：`next-fullstack` / `react-fastapi` 声明 shadcn/ui v3 官方安装范式（`components.json` + `@import "tailwindcss"` + `--primary`/`--radius` CSS 变量 + 源码拷贝进 `src/components/ui/`、`shadcn add`、禁止 `babel-plugin-import`）；`vue-django` 声明 Naive UI 2.x 官方范式（不导入任何 CSS、`n-config-provider :theme-overrides` + `GlobalThemeOverrides` 集中 `theme.ts`、`zhCN`/`dateZhCN` locale）；`framework-gate` 注册表与 `ui-stack-conformance` 同步新增 shadcn / naive-ui 门禁（反模式拦截：`babel-plugin-import`、`naive-ui/dist` 全量 CSS 导入），并明确「官方范式优先」原则——新 UI 栈接入必须先查官方 starter/quickstart/template 再生成瘦 DEMO。
- `1.8.0`：Element Plus 2.x 与 Ant Design v6 官方范式（ui-stack-conformance）：新增 `vue-element-plus-nitro` Blueprint（Vue3 + Vite + Element Plus PC 管理端 + Nitro + Drizzle + SQLite/Turso + Vercel AI SDK，内置 pnpm workspace + `apps/web` starter：完整引入 `element-plus/dist/index.css` + `app.use(ElementPlus)`、`--el-*` 设计令牌、`el-config-provider` zhCn locale、Volar `element-plus/global` 类型）；`react-springboot` 升级为 Ant Design v6 并内置 `frontend/` starter（ConfigProvider `theme.token` + `zhCN`/dayjs locale、v6 弃用 API 清单、拦截 `@ant-design/v5-patch-for-react-19`）；生成器文本模板扩展 `.tsx/.jsx`，确保 React starter 的 `{{PROJECT_NAME}}` 等占位符正确渲染。
- `1.7.0`：新增 Vant 4 官方范式（ui-stack-conformance）：`uni-app-nitro` Blueprint 升级为 `vant + uni-ui`，内置 uni-app 工作区 + mobile 应用 starter（`apps/mobile`），按 Vant 4 官方 quickstart / vant-demo 范式初始化（`vant/lib/index.css` + `app.use()` 按需注册、`--van-*` 设计令牌、`van-config-provider`、`showToast`/`showDialog` 函数式 API），并拦截反模式（`babel-plugin-import`、全量 css 与 VantResolver 混用）。
- `1.6.0`：新增 UI 栈官方范式校验（ui-stack-conformance）：Nuxt UI 系 starter 按 Nuxt UI v4 / Tailwind v4 官方模板（dashboard/chat）范式初始化（`@import "tailwindcss" theme(static)` + `@import "@nuxt/ui"` + `@theme static` 品牌全色阶、`ui.colors` 语义色映射、`ui.theme.colors`、`tailwindcss` 与 `@iconify-json/*` 依赖、`app/error.vue`），并自动拦截偏离官方范式的生成品（遗留 `--mc-*` 令牌、缺失 tailwindcss 等）。
- `1.5.0`：新增框架组件门禁（framework-component-gate）：DESIGN.md 自动登记 Nuxt UI v4 约束（`UFormGroup` → `UFormField`、@nuxt/icon CSS 模式说明），`validate.py` 扫描生成项目源码拦截废弃组件名；演示账号内置到 mock 用户库，页面展示的演示凭据可直接登录。
- `1.4.0`：新增 `uni-app-nitro` Blueprint，补齐移动端首推组合、管理后台选型询问与运行验证完成标准。
- `1.3.0`：新增 react-springboot 与 uni-app 移动端首选，引入 Blueprint `layout` 目录契约、栈级启动命令、多应用独立 UI/样式库，并统一验证版本号。

## 这个技能是什么

AI Bootstrap 是一个 **AI 原生工程上下文注入系统**，不是传统的项目脚手架。

传统脚手架生成的是代码模板；AI Bootstrap 生成的是 AI 认知地图。它在项目启动、技术选型或 AI Agent 进场之前，为项目建立完整、可维护、可验证的工程上下文，让人类开发者和多个 AI Agent 从第一天起就在同一套信息基础上协作。

每次 Bootstrap 可以理解为一次“AI 与项目的第一次握手”：检测项目现状、确认技术栈、生成治理文件、记录设计决策、验证输出完整性，最后把项目状态交给后续开发流程。

## 它解决什么问题

- **AI 每次进项目都从零猜测**：没有统一入口，Agent 不知道技术栈、架构约束、可修改边界和当前进度。
- **治理文件散落、规则不一致**：AGENTS、项目 DNA、设计文档、ADR、记忆文件没有统一结构和路由关系。
- **技术选型只停留在对话里**：方案、理由、代价和迁移触发条件没有落盘，后来者不知道为什么这么选。
- **多 Agent 协作各自为政**：Codex、Claude Code、Cursor 等没有共享的角色定义和上下文读取顺序。
- **前端设计缺少语义化基线**：页面直接散落颜色和组件样式，难以长期维护。
- **新项目缺少可演示链路**：初始化后只有一个空壳，连“登录 → 工作台 → 新建/编辑”都跑不起来。

## 核心理念

- **Context Before Code**：生成任何代码前，先建立完整的工程上下文。
- **Detection Before Questions**：能自动检测的，绝不询问用户。
- **Governance Over Scaffolding**：治理体系优于代码模板。
- **Multi-Agent Native**：从第一天起支持多 Agent 协作。

## 适合场景

| 场景 | 说明 |
|------|------|
| 全新项目冷启动 | 在空目录初始化时，生成 AI 可读的治理文件、技术栈决策、设计令牌规范和项目骨架 |
| 现有项目注入治理 | 接手或改造已有项目时，通过深度检测识别技术栈，补齐缺失的治理文件 |
| 技术栈决策 | 技术选型不明确时，提供典型方案卡片、推荐理由、替代方案和代价说明 |
| 多 Agent 协作 | 为 Codex / Claude Code / Cursor / Trae / Windsurf / Gemini CLI 生成统一角色和路由 |
| AI 原生 MVP | 通过 Nuxt AI Fullstack Blueprint 快速获得 AI 应用骨架和 mock-first 基础功能 |
| 产品设计系统起步 | 在生成前确认设计令牌、主题入口和组件基线，避免 UI 库默认主题直接成为产品视觉 |
| 团队规范化开发 | 统一 SDD 阶段目录、ADR 和项目 DNA，让文档结构与工程流程对齐 |

## 不适合场景

- 需要直接生成完整业务 CRUD、页面和业务代码的脚手架需求。
- 项目已经治理完善且稳定，不想引入额外文件。
- 希望无条件覆盖已有代码或治理文件。AI Bootstrap 默认保护已有文件，只有显式 `--force` 才允许覆盖治理文件，且始终不覆盖用户代码。
- 希望强制所有项目使用同一种架构风格。Blueprints 保留各自的架构选择。
- 希望用 MEMORY 文件替代 Git、需求系统或 Issue 跟踪。

## 工作模式

AI Bootstrap 支持三种入口模式，统一走同一套生命周期：

```text
Detect ──▶ Analyze ──▶ Resolve ──▶ Generate ──▶ Verify ──▶ Complete
```

| 模式 | 触发条件 | 主要流程 |
|------|----------|----------|
| 全新项目 Bootstrap | 目标目录为空 | 环境检测 → 技术选型确认 → 生成治理文件与项目骨架 → 验证 |
| 现有项目注入治理 | 目标目录已有代码 | 深度检测 → 识别技术栈 → 匹配 Blueprint → 补齐缺失治理文件 → 验证 |
| 快速 Blueprint | 用户已明确技术栈 | 加载指定 Blueprint → 复述完整组合 → 确认 → 生成 → 验证 |

进度判定规则：

```text
检测目标目录 → detect.py 运行结果
  ├── 已存在 docs/PROJECT_PROFILE.md → 项目已 Bootstrap，询问是否升级或重新生成
  ├── 已有 package.json / pyproject.toml / go.mod 等 → 先检测，再询问是否注入治理
  └── 空目录 → 全新项目，进入 Bootstrap 流程
```

## 使用方式

### 在 Codex 中直接使用

对 Codex 提出需求即可触发本技能，例如：

```text
用 ai-bootstrap 初始化 /tmp/my-app，技术栈选 Nuxt AI Fullstack
```

```text
给 /tmp/existing-project 注入 AI 治理体系，检测现有技术栈并生成治理文件
```

技能会按照检测 → 选型确认 → 生成 → 验证的流程执行。若技术栈不明确，它会先展示方案卡片，在得到确认前不会写入项目。

### 全新项目快速开始

```bash
SKILL_DIR=/Users/lawrence/6D/AiSkills/TrainingDevelop/skills/ai-bootstrap

# 1. 检测目标目录与环境
python3 "$SKILL_DIR/scripts/detect.py" --dir ./my-app --deep

# 2. 通过 Wizard 选择 Blueprint 并确认参数
python3 "$SKILL_DIR/scripts/wizard.py" --dir ./my-app

# 3. 先预览再正式生成
python3 "$SKILL_DIR/scripts/generate.py" \
  --dir ./my-app \
  --blueprint nuxt-ai-fullstack \
  --name MyApp \
  --agents codex,cursor \
  --platform codex \
  --dry-run

python3 "$SKILL_DIR/scripts/generate.py" \
  --dir ./my-app \
  --blueprint nuxt-ai-fullstack \
  --name MyApp \
  --agents codex,cursor \
  --platform codex

# 4. 自检验证
python3 "$SKILL_DIR/scripts/validate.py" --dir ./my-app
```

### 现有项目注入治理

```bash
SKILL_DIR=/Users/lawrence/6D/AiSkills/TrainingDevelop/skills/ai-bootstrap

# 1. 深度检测现有项目
python3 "$SKILL_DIR/scripts/detect.py" --dir ./existing-project --deep

# 2. 先用 auto 模式预览
python3 "$SKILL_DIR/scripts/generate.py" \
  --dir ./existing-project \
  --blueprint auto \
  --dry-run

# 3. 确认后正式生成（默认只补缺失文件）
python3 "$SKILL_DIR/scripts/generate.py" \
  --dir ./existing-project \
  --blueprint auto

# 4. 验证
python3 "$SKILL_DIR/scripts/validate.py" --dir ./existing-project
```

对已有治理文件，只有显式添加 `--force` 才会覆盖；用户现有代码文件始终不会被覆盖。

### 脚本索引

| 脚本 | 用途 | 核心参数 |
|------|------|----------|
| `scripts/detect.py` | 检测目标目录、运行环境、技术栈、包管理器、架构信号 | `--dir`，可选 `--json`、`--deep` |
| `scripts/wizard.py` | 交互式 Blueprint 选择与参数收集 | `--dir`，可选 `--mode quick\|normal\|advanced`、`--blueprint`、`--dry-run` |
| `scripts/generate.py` | 生成治理文件、设计令牌规范、项目骨架与 starter | `--dir`、`--blueprint`，可选 `--name`、`--description`、`--agents`、`--platform`、`--dry-run`、`--force`、`--starter`、`--no-starter` |
| `scripts/validate.py` | 自检验证生成结果 | `--dir`，可选 `--fix`、`--json` |

## 技术选型交互契约

初始化新项目时，技术栈选择是明确的“方案选择 → 用户确认 → 生成”流程，而不是隐含推断。

用户未给出明确技术栈时：

1. 先检测目录和运行环境，检测结果只用于缩小范围。
2. 展示 `references/stack-presets.md` 中的典型方案卡片：适用场景、完整组合、优势、代价和迁移触发条件。
3. 至少确认五个问题：目标端是 PC、H5、小程序还是 App；第一版更看重 AI 原生、Demo 速度、企业扩展还是模型/数据能力；是否希望前后端统一语言；部署目标是本地、Serverless 还是 Docker/云服务器；是否同时需要独立管理后台 / PC Web。
4. 给出一个推荐方案和至少一个替代方案，说明推荐理由与主要代价。
5. 复述完整组合：前端、后端、AI SDK、数据库、ORM、部署平台、包管理器。
6. 若包含前端，同时确认样式方案、图标方案、官方主题入口和设计令牌实现入口。
7. 用户确认前，不得正式生成或修改治理文件和项目代码。

生成成功后，必须持久化两份决策：

- `docs/00-research/stack-decision.md`：记录选择来源、Blueprint、完整组合、理由、代价和迁移触发条件。
- `docs/00-research/design-token-spec.md`：记录主题入口、语义令牌、组件基线和首屏验收标准。

已有文件不得覆盖；变更应追加新决策或进入 ADR。

## Blueprint 体系

Blueprint 是“技术栈 + 架构风格 + 设计系统入口 + 可选 starter”的完整定义，位于 `templates/blueprints/`。

| Blueprint ID | 定位 | 典型组合 |
|--------------|------|----------|
| `nuxt-ai-fullstack` | AI 原生 MVP、企业工作台、内容生成 | Nuxt 4 + Nuxt UI + Nitro + Vercel AI SDK + SQLite/Turso + Drizzle |
| `uni-app-nitro` | 移动端 H5/小程序/App + Nitro API | uni-app + Vue3 + uni-ui + Nitro + SQLite/Turso + Vercel AI SDK |
| `vue-element-plus-nitro` | Vue3 PC 管理端 + Nitro API | Vue 3 + Vite + Element Plus 2.x + Nitro + SQLite/Turso + Vercel AI SDK |
| `next-fullstack` | React 生态、标准 SaaS、团队协作 | Next.js + NestJS + PostgreSQL + Prisma + Auth.js |
| `react-fastapi` | Python AI、数据处理、模型服务 | React + FastAPI + PostgreSQL |
| `react-springboot` | 企业级系统、团队协作、合规 | React 19 + Vite + Ant Design 6 + Spring Boot + PostgreSQL/MySQL |
| `vue-django` | 内容管理、企业后台、Python 业务系统 | Vue/Nuxt + Django + PostgreSQL |
| `go-microservice` | 高吞吐 API、基础设施、服务拆分 | Go + Gin + PostgreSQL + gRPC |
| `rust-axum-api` | 高性能 API、类型安全后端 | Rust + Axum + SQLite |
| `python-ml-service` | 模型实验、推理服务、数据管线 | FastAPI + PyTorch + SQLite/PostgreSQL |

### 多应用与移动端

同一个项目可以包含多个独立前端应用。PC 与移动端默认不共用一套前端方案，每个应用可以独立选择 UI 库和样式库，只共享产品级语义令牌：

| 阵营 | 首选组件库 | 备选 |
|---|---|---|
| PC Vue | Nuxt 4 + Nuxt UI | Element Plus、Naive UI、PrimeVue、Ant Design Vue |
| PC React | Next.js + shadcn/ui 或 Ant Design | Mantine、Arco Design、MUI |
| PC Svelte / Solid | SvelteKit + shadcn-svelte；SolidJS + Solid UI | Skeleton、Kobalte、Bits UI、SUID |
| 移动端 | uni-app + Vue3 + uni-ui | Wot Design Uni、uview-plus、NutUI |
| 移动端 React | Taro + React + Ant Design Mobile | React Vant、NutUI React |

移动端项目首选 uni-app，一次开发覆盖 H5、小程序和 App；落地时作为独立应用与现有后端 Blueprint 组合，不复用 PC 前端方案。

默认优先级：AI 相关功能优先使用 `nuxt-ai-fullstack`；企业级系统优先使用 `react-springboot`。

每个 Blueprint 至少声明 `stack`、`architecture` 和 `layout`；包含前端时必须声明 `design_system`，用于生成设计令牌规范。多应用项目在 `stack-decision.md` 和 `design-token-spec.md` 中按应用分别声明独立 UI/样式库与主题入口。Blueprint 中的 `starter` 字段控制是否在全新项目中复制基础功能基线。

部分 Blueprint 会通过 `skills` 声明官方推荐 AI 技能。例如 Nuxt UI 提供 `/nuxt-ui` 技能，可通过 `npx skills add nuxt/ui` 安装；生成器会写入 `AGENTS.md`、`README.md` 和 `PROJECT_PROFILE.md`。

### 目录结构契约

治理层（`AGENTS.md`、`docs/`、`.ai-bootstrap/`）在所有 Blueprint 间保持统一；应用源码目录由每个 Blueprint 的 `layout` 声明，并必须符合对应技术栈的官方约定。生成器会把目录表写入 `README.md`、`DESIGN.md` 和 `PROJECT_PROFILE.md`。现有项目不强制重构，检测后记录实际结构，AI 按现状工作。

## 生成物

Bootstrap 保持根目录瘦身：根目录只保留工程入口和 Agent 路由，SDD 文档按阶段归档到 `docs/`，机器元数据放入 `.ai-bootstrap/`。

```text
project/
├── AGENTS.md                         # Agent 路由层 + 权限矩阵
├── README.md                         # 项目说明（全新项目）
├── .gitignore                        # Git 忽略规则（全新项目）
├── docs/
│   ├── PROJECT_PROFILE.md            # 项目 DNA（唯一事实来源）
│   ├── DESIGN.md                     # 设计文档 + 架构约束
│   ├── ai/MEMORY.md                  # AI 记忆与协作状态
│   ├── 00-research/                  # 调研、stack-decision、design-token-spec
│   ├── 01-requirements/              # 需求
│   ├── 02-specs/                     # 规格
│   ├── 03-plans/                     # 实施计划、current、backlog
│   ├── 04-reviews/                   # 审查记录
│   ├── 05-verification/              # 验证与验收证据
│   └── 06-decisions/
│       ├── adr/                      # 架构决策记录
│       └── decisions/                # 非架构类决策日志
└── .ai-bootstrap/
    └── bootstrap-manifest.yaml       # 机器可读清单
```

## 基础功能基线

`nuxt-ai-fullstack` Blueprint 默认携带 mock-first 基础功能基线（`templates/starter/nuxt-basic-auth/`）：

- JWT + author 鉴权：登录、注册、当前用户、退出和前端路由守卫。
- 客户项目管理：列表、新建、编辑和状态迁移。
- 双 adapter 契约：页面 → composable → feature port，Mock 与 API 实现同一套领域操作。
- 升级路径：替换服务端 JWT/scrypt、按 `author_id` 隔离数据、把 mock 分支替换为 `$fetch` 调用。

需要跳过 starter 时使用 `--no-starter`，强制开启时使用 `--starter`。

## 多 Agent 支持

`--agents` 定义完整的参与 Agent 集合，`--platform` 定义主 AI 平台。同一套角色会同时写入：

- `AGENTS.md`：角色、权限和操作约束。
- `docs/PROJECT_PROFILE.md`：作为项目 DNA 的一部分。

标准上下文读取顺序：

```text
AGENTS.md → docs/PROJECT_PROFILE.md → docs/DESIGN.md →
docs/ai/MEMORY.md → docs/06-decisions/adr/INDEX.md →
docs/03-plans/current.md
```

## 验证与质量保障

`validate.py` 会检查：

- 必需治理文件、SDD 阶段目录和 manifest 是否齐全。
- Blueprint 声明的技术栈与生成文档是否一致。
- AGENTS 角色定义与项目 DNA 是否一致。
- ADR 索引、初始 ADR、计划文件是否初始化。
- 现有项目是否未覆盖已有代码，dry-run 是否没有实际写入。
- 生成文件中是否残留未渲染模板标记。
- 设计令牌规范和前端首屏验收是否已落盘。

回归测试位于 `tests/test_pipeline.py`：

```bash
python3 -m unittest tests/test_pipeline.py -v
```

## 技能目录结构

```text
ai-bootstrap/
├── SKILL.md                          # 执行规范、流程、交互契约
├── agents/openai.yaml                # 默认 Agent 声明
├── references/
│   ├── architecture-proposal.md      # 架构设计参考
│   ├── blueprint-guide.md            # Blueprint 开发规范
│   ├── stack-presets.md              # 典型技术方案卡片
│   ├── design-token-guide.md         # 设计令牌规范指南
│   └── basic-feature-baseline.md     # mock-first 基础功能说明
├── scripts/
│   ├── detect.py                     # 项目环境与技术栈检测
│   ├── wizard.py                     # 交互式选型向导
│   ├── generate.py                   # 治理文件与骨架生成
│   ├── validate.py                   # 自检验证
│   ├── deep_detect.py                # 深度检测实现
│   ├── layout.py                     # 输出目录布局
│   └── yaml_utils.py                 # 依赖无关 YAML 子集解析
├── templates/
│   ├── governance/                   # AGENTS、PROJECT_PROFILE、DESIGN、MEMORY、ADR
│   ├── project/                      # 新项目 README、.gitignore
│   ├── blueprints/                   # 8 个内置 Blueprint
│   ├── starter/nuxt-basic-auth/      # mock-first 基础功能 starter
│   └── prompt/                       # Bootstrap 完成提示
└── tests/
    └── test_pipeline.py              # 端到端回归测试
```

## 参考资料

| 文件 | 何时阅读 | 用途 |
|------|----------|------|
| [SKILL.md](./SKILL.md) | 每次使用 | 完整执行规范和工作流 |
| [architecture-proposal.md](./references/architecture-proposal.md) | 首次使用 | 系统架构设计契约 |
| [blueprint-guide.md](./references/blueprint-guide.md) | 创建 Blueprint 时 | Blueprint 开发规范 |
| [stack-presets.md](./references/stack-presets.md) | 新项目选型时 | 典型方案、取舍与迁移触发条件 |
| [design-token-guide.md](./references/design-token-guide.md) | 技术栈确认后、生成前 | 设计令牌层次和主题入口 |
| [basic-feature-baseline.md](./references/basic-feature-baseline.md) | 使用 Nuxt starter 时 | 鉴权与项目管理基线 |

## 开发与扩展

需要新增技术栈时，在 `templates/blueprints/` 添加一个 YAML 文件，遵循 `references/blueprint-guide.md`：

- 使用语义化版本号，声明完整 `stack` 与 `architecture`。
- 包含前端时声明 `design_system`：UI 库、样式方案、图标、主题入口和组件基线。
- 可选声明 `starter`，并在 `templates/starter/<template_dir>/` 提供基础功能文件。
- 不包含凭据、环境变量值或不可移植的绝对路径。
- 为每个新 Blueprint 增加生成与验证回归测试。

兼容性约束：现有输出路径在 v1.x 内保持稳定；路径迁移必须同时更新生成器、验证器、SKILL.md 和回归测试，并以 ADR 记录迁移决策。
