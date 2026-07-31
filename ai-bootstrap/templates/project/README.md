# {{PROJECT_NAME}}

> {{PROJECT_DESCRIPTION}}

---

## 技术栈

| 层次 | 技术 |
|------|------|
| 前端 | {{FRONTEND_FRAMEWORK}} |
| 后端 | {{BACKEND_FRAMEWORK}} |
| 数据库 | {{DATABASE_TYPE}} |
| 部署 | {{DEPLOYMENT_TYPE}} |

## 快速开始

```bash
# 安装依赖
{{PACKAGE_MANAGER}} install

# 启动开发服务器
{{PACKAGE_MANAGER}} dev
```

## 项目结构

```
├── AGENTS.md              # AI Agent 路由
├── docs/                  # SDD 与工程治理文档
│   ├── 00-research/       # 调研
│   ├── 01-requirements/   # 需求
│   ├── 02-specs/          # 规格
│   ├── 03-plans/          # 计划与任务
│   ├── 04-reviews/        # 审查
│   ├── 05-verification/   # 验证
│   ├── 06-decisions/      # ADR 与决策记录
│   ├── DESIGN.md          # 设计文档
│   └── PROJECT_PROFILE.md # 项目 DNA
├── .ai-bootstrap/         # Bootstrap 元数据
└── src/                   # 源代码
```

## 治理

本项目使用 **AI Bootstrap** 进行工程上下文管理。
所有 AI Agent 在开始工作前应读取 AGENTS.md 中的 Context Router。

## 许可证

MIT
