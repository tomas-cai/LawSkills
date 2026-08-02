---
bootstrap_version: {{BOOTSTRAP_VERSION}}
blueprint_id: {{BLUEPRINT_ID}}
generated: {{CREATED_DATE}}
---

# AGENTS.md — AI Agent Routing Layer

> 此文件定义了哪些 AI Agent 可以操作本项目，以及各自的角色、权限和约束。
> **所有 Agent 在开始工作前必须读取此文件。**

---

{{PROJECT_SKILLS_SECTION}}

## Agent 定义

{{AGENT_DEFINITIONS}}

---

## 上下文读取顺序 (Context Router)

context_router: standard
router_order: AGENTS.md → docs/PROJECT_PROFILE.md → docs/DESIGN.md → docs/ai/MEMORY.md → docs/06-decisions/adr/INDEX.md → docs/03-plans/current.md

所有 Agent 在开始工作前，按以下顺序读取上下文文件：

```
1. AGENTS.md                              — 你的角色和权限 (当前文件)
2. docs/PROJECT_PROFILE.md                — 项目 DNA (唯一事实来源)
3. docs/DESIGN.md                         — 设计文档和架构约束
4. docs/ai/MEMORY.md                      — AI 记忆和当前状态
5. docs/06-decisions/adr/INDEX.md         — 最近的架构决策
6. docs/03-plans/current.md               — 当前任务
```

---

## 文件标签约定

Agent 生成或修改的文件应使用标签标记：

| 标签 | 含义 |
|------|------|
| `// @agent: codex` | 由 Codex 创建/维护 |
| `// @agent: cursor` | 由 Cursor 创建/维护 |
| `// @agent: claude-code` | 由 Claude Code 创建/维护 |
| `# @agent: <name>` | Python/Ruby 等语言使用 |

---

## 治理规则

1. **不可变性**: docs/PROJECT_PROFILE.md 的 DNA 部分不可随意修改，变更必须经 ADR 审批
2. **ADR 优先**: 任何架构变更必须先创建 ADR，再实施修改
3. **记忆同步**: Agent 完成工作后，更新 docs/ai/MEMORY.md 记录状态
4. **冲突解决**: 多 Agent 并发修改同一文件时，最后写入者获胜，并在 docs/ai/MEMORY.md 记录
5. **定期验证**: 每次重大变更后，运行 `validate.py` 检查治理文件完整性

---

## Blueprint 信息

| 属性 | 值 |
|------|------|
| **Blueprint ID** | {{BLUEPRINT_ID}} |
| **Blueprint 版本** | {{BLUEPRINT_VERSION}} |
| **Bootstrap 版本** | {{BOOTSTRAP_VERSION}} |
| **生成日期** | {{CREATED_DATE}} |
