---
# === AI Project DNA ===
# 此文件是项目的唯一事实来源。
# 任何 AI Agent 在开始工作前必须读取此文件。
# 修改此文件须经过架构评审并记录 ADR。

dna:
  id: "{{PROJECT_ID}}"
  name: "{{PROJECT_NAME}}"
  description: "{{PROJECT_DESCRIPTION}}"
  version: "{{PROJECT_VERSION}}"
  created: "{{CREATED_DATE}}"
  classification: "internal"

  tech_stack:
    primary_language: "{{PRIMARY_LANGUAGE}}"
    frontend:
      framework: "{{FRONTEND_FRAMEWORK}}"
    backend:
      framework: "{{BACKEND_FRAMEWORK}}"
      orm: "{{ORM}}"
    database:
      primary:
        type: "{{DATABASE_TYPE}}"
        version: "{{DATABASE_VERSION}}"
    auth:
      provider: "{{AUTH_PROVIDER}}"
    deployment:
      type: "{{DEPLOYMENT_TYPE}}"
    package_manager: "{{PACKAGE_MANAGER}}"
    monorepo: "{{MONOREPO_TOOL}}"

  architecture:
    style: "{{ARCHITECTURE_STYLE}}"
    pattern: "{{ARCHITECTURE_PATTERN}}"

  design_principles:
{{DESIGN_PRINCIPLES_YAML}}

  coding_convention:
{{CODING_CONVENTION_YAML}}

  governance:
    bootstrap_version: "{{BOOTSTRAP_VERSION}}"
    blueprint_id: "{{BLUEPRINT_ID}}"
    agents:
{{AGENTS_YAML}}
    context_router: "standard"
---

# {{PROJECT_NAME}}

> {{PROJECT_DESCRIPTION}}

---

## 项目概览

| 属性 | 值 |
|------|------|
| **项目名称** | {{PROJECT_NAME}} |
| **版本** | {{PROJECT_VERSION}} |
| **创建日期** | {{CREATED_DATE}} |
| **Blueprint** | {{BLUEPRINT_ID}} v{{BLUEPRINT_VERSION}} |
| **架构风格** | {{ARCHITECTURE_STYLE}} / {{ARCHITECTURE_PATTERN}} |

### 技术栈

| 层次 | 技术 | 版本 |
|------|------|------|
| 前端 | {{FRONTEND_FRAMEWORK}} | 最新 |
| 后端 | {{BACKEND_FRAMEWORK}} | 最新 |
| 数据库 | {{DATABASE_TYPE}} | {{DATABASE_VERSION}} |
| ORM | {{ORM}} | — |
| 认证 | {{AUTH_PROVIDER}} | — |
| 部署 | {{DEPLOYMENT_TYPE}} | — |
| 包管理器 | {{PACKAGE_MANAGER}} | — |

### Agent 配置

| Agent | 角色 |
|------|------|
{{AGENT_SUMMARY_ROWS}}

---

## DNA 变更记录

| 版本 | 日期 | ADR | 描述 | 作者 |
|------|------|-----|------|------|
| {{PROJECT_VERSION}} | {{CREATED_DATE}} | ADR-0001 | 初始 DNA 定义 | AI Bootstrap |
