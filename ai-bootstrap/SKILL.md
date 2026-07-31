---
name: ai-bootstrap
description: >
  AI Native Engineering Bootstrap System.
  为 AI 建立长期、统一、可治理的软件工程上下文。
  当用户需要初始化新项目、为现有项目注入 AI 治理体系、选择技术栈组合 Blueprint、
  生成治理文件（AGENTS.md / PROJECT_PROFILE.md / DESIGN.md / MEMORY.md / ADR）、
  或在 AI Agent 开始工作前统一上下文时触发。
  也可在已部分初始化的项目基础上从中段执行（如已有项目检测 → 生成治理）。
  特别适配多 Agent 协作场景（Codex / Claude Code / Cursor / Trae / Windsurf / Gemini CLI）。
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
4. 运行 Wizard（仅询问无法检测的信息）
5. 运行 generate.py 生成治理文件 + 项目骨架
6. 运行 validate.py 自检验证
```

### 模式 2: 现有项目注入治理（从检测开始）

用户已有项目代码，需要注入 AI 治理体系。

```
1. 运行 detect.py 检测已有项目
2. 自动识别技术栈、框架、架构
3. 匹配最接近的 Blueprint
4. 生成治理文件（不覆盖现有代码）
5. 验证兼容性
```

### 模式 3: 快速 Blueprint（从蓝图开始）

用户已有明确的技术栈选择。

```
1. 用户指定 Blueprint ID
2. 加载 Blueprint 定义
3. 询问项目名称、描述等基本信息
4. 生成治理文件 + 项目骨架
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
| `templates/blueprints/` | Blueprint 定义文件 | 按需加载 |
| `templates/prompt/bootstrap-complete.md` | Bootstrap 完成提示 | 流程完成 |

## Blueprint 定义

Blueprint 定义在 `templates/blueprints/` 目录下，每个 Blueprint 一个文件：

### 已有 Blueprint

- `next-fullstack.yaml` — Next.js + NestJS + PostgreSQL + DDD 架构
- `react-fastapi.yaml` — React + FastAPI + PostgreSQL
- `vue-django.yaml` — Vue + Django + PostgreSQL
- `go-microservice.yaml` — Go + Gin + PostgreSQL + gRPC
- `rust-axum-api.yaml` — Rust + Axum + SQLite
- `python-ml-service.yaml` — Python + FastAPI + PyTorch

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
```

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
│   ├── 00-research/                  # 调研
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

## 参考文件索引

| 文件 | 何时读 | 用途 |
|------|--------|------|
| `references/architecture-proposal.md` | 首次使用 | 完整的架构设计蓝图（18 章） |
| `references/blueprint-guide.md` | 创建 Blueprint 时 | Blueprint 开发规范 |

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
- 用户明确指定 → 确认后使用

如无匹配或用户需要自定义，询问关键技术选择：
- 前端框架
- 后端框架
- 数据库
- 架构风格

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

如果用户指定 `--dry-run`，先预览再确认。

#### Step 5: 验证

```bash
python3 <skill-dir>/scripts/validate.py --dir /path/to/project
```

解读验证报告：
- passed → 告知用户完成
- warning → 列出警告项，建议修复
- failed → 修复问题后重新验证

#### Step 6: 完成

向用户提供：
1. Bootstrap Summary（生成的文件清单）
2. 项目上下文摘要（技术栈、Agent 角色、架构风格）
3. 下一步建议（"现在可以用 Codex 开始开发了"）

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
- [ ] docs/06-decisions/adr/ 包含 ADR 索引和初始 ADR
- [ ] docs/03-plans/ 包含 current.md
- [ ] docs/04-reviews/ 包含 INDEX.md
- [ ] Blueprint 声明的技术栈与生成的治理文件一致
- [ ] 对现有项目，未覆盖任何已有代码
- [ ] 对现有治理文件默认跳过，只有 `--force` 才覆盖
- [ ] dry-run 模式不产生实际写入
- [ ] 生成文件不包含未渲染模板标记
- [ ] .ai-bootstrap/bootstrap-manifest.yaml 已生成
