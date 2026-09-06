# AI 工程治理与项目初始化 Skill 体系

## 系列定位

为 AI Agent 建立统一、可维护、可验证的项目上下文与文档治理结构。该系列目前由两个互补 Skill 组成，但不是强制串行流水线。

## Skill 组成

| Skill | 核心职责 | 适用场景 |
|---|---|---|
| `project-scaffold` | 快速生成项目文档治理骨架、设计规范和阶段目录 | 需要标准目录，或只想补齐文档治理结构 |
| `ai-bootstrap` | 检测项目、选择技术 Blueprint、生成 AI 治理文件、starter 与验证结果 | 新项目初始化、既有项目注入 AI 治理、多 Agent 协作 |

## 选择逻辑

```text
需要项目文档目录治理？
├── 是，需求轻量/只补结构 → project-scaffold
└── 是，需要技术选型、AI 上下文、Blueprint 和验证 → ai-bootstrap
```

两者都可能生成 `AGENTS.md`、`DESIGN.md` 等治理文件，不建议对同一项目连续无差别执行，以免重复生成或产生规范冲突。

## `project-scaffold` 输出

```text
project/
├── AGENTS.md
├── docs/
│   ├── DESIGN.md
│   ├── 00-research/
│   ├── 01-requirements/
│   ├── 02-specs/
│   ├── 03-plans/
│   ├── 04-reviews/
│   ├── 05-verification/
│   └── 06-decisions/
├── packages/design-tokens/       # Monorepo 时生成
└── README.md
```

适合先建立文档路由和项目设计规范，不负责完整技术栈决策，也不替代项目代码开发。

## `ai-bootstrap` 输出

`ai-bootstrap` 通过 `Detect → Analyze → Resolve → Generate → Verify → Complete` 工作流，按 Blueprint 生成：

- `AGENTS.md`、`PROJECT_PROFILE.md`、`DESIGN.md`、`MEMORY.md`、ADR；
- `docs/00-research/stack-decision.md` 和设计令牌规范；
- 与技术栈匹配的项目骨架或瘦 Demo；
- 检测、生成和验证报告。

用户未确认技术选型前，不应正式写入项目治理文件或代码。

## 协作边界

- 两个 Skill 不共享隐藏状态，协作依赖项目文件和生成报告。
- `project-scaffold` 解决目录与文档治理的最小闭环。
- `ai-bootstrap` 解决从环境检测到技术选型、生成和验证的完整闭环。
- 已经使用 `ai-bootstrap` 的项目，不要再用 `project-scaffold` 覆盖同一批治理文件；若缺少目录，应先检测后补齐。
