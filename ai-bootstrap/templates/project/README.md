# {{PROJECT_NAME}}

> {{PROJECT_DESCRIPTION}}

---

## 技术栈

| 层次 | 技术 |
|------|------|
| 前端 | {{FRONTEND_FRAMEWORK}} {{FRONTEND_VERSION}} |
| UI 库 | {{FRONTEND_UI_LIBRARY}} |
| 后端 | {{BACKEND_FRAMEWORK}} {{BACKEND_VERSION}} |
| AI SDK | {{AI_SDK}} |
| 数据库 | {{DATABASE_TYPE}} |
| 生产数据库 | {{DATABASE_PRODUCTION}} |
| 部署 | {{DEPLOYMENT_PLATFORM}} |

设计令牌与主题入口见 [`docs/00-research/design-token-spec.md`](docs/00-research/design-token-spec.md)。

## 快速开始

```bash
# 安装依赖
{{PROJECT_INSTALL_COMMAND}}

# 启动开发服务器
{{PROJECT_DEV_COMMAND}}

# 运行测试
{{PROJECT_TEST_COMMAND}}
```

{{PROJECT_SKILLS_SECTION}}

## 项目结构

治理层保持统一：

```text
├── AGENTS.md              # AI Agent 路由
├── docs/                  # SDD 与工程治理文档
├── .ai-bootstrap/         # Bootstrap 元数据
└── 应用源码                # 按技术栈官方约定组织
```

应用源码目录：

{{PROJECT_LAYOUT_TABLE}}

{{PROJECT_LAYOUT_CONVENTIONS}}

## 治理

本项目使用 **AI Bootstrap** 进行工程上下文管理。
所有 AI Agent 在开始工作前应读取 AGENTS.md 中的 Context Router。

## 许可证

MIT
