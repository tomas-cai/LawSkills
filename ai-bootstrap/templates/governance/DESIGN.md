---
bootstrap_version: {{BOOTSTRAP_VERSION}}
blueprint_id: {{BLUEPRINT_ID}}
generated: {{CREATED_DATE}}
---

# DESIGN.md — 设计文档

> 此文件记录项目的设计决策和架构约束。
> 所有 Agent 在修改代码前应参考此文档。

> 前端设计令牌基线见 `docs/00-research/design-token-spec.md`。UI 库默认主题不得直接作为产品最终视觉系统。

---

## 架构设计

| 属性 | 值 |
|------|------|
| **架构风格** | {{ARCHITECTURE_STYLE}} |
| **架构模式** | {{ARCHITECTURE_PATTERN}} |

### 架构边界

{{ARCHITECTURE_BOUNDARIES}}

---

## 架构约束

{{ARCHITECTURE_CONSTRAINTS}}

## 项目目录契约

应用源码目录必须遵循对应技术栈的官方约定：

{{PROJECT_LAYOUT_TABLE}}

{{PROJECT_LAYOUT_CONVENTIONS}}

### 前端 Mock 与真实 API 的数据边界

当项目包含前端并预计接入后端 API 时，页面和组件不得直接持有 mock 数据或 HTTP 细节；应通过 feature-specific composable / service 和轻量 port 访问数据。开发阶段可由 Mock adapter 实现该 port，联调阶段再替换为 API adapter。

仅限一次性静态展示、没有持久化、权限、审核状态或异步流程的原型，才允许页面级 mock。不要为此引入通用 Repository 框架、全局数据层或复杂依赖注入；接口应按业务功能保持小而具体。

若产品包含用户生成数据或异步业务状态，默认提供基础鉴权（可 mock-first），并按数据所有者隔离访问；鉴权与数据新建/编辑应通过同一 port 契约实现。

---

## 框架约束 (Framework Constraints)

> UI 库/框架版本升级的已知坑位在此登记，作为 Agent 改代码前的强制约束；`validate.py` 会对其中可自动扫描的条目执行门禁。

{{FRAMEWORK_CONSTRAINTS}}

---

## 关键工程实践

{{ENGINEERING_PRACTICES}}

---

## 技术债务与注意事项

> 初始状态：无已知技术债务。

---
