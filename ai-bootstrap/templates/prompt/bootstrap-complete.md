# AI Bootstrap 完成

项目 **{{PROJECT_NAME}}**（slug：`{{PROJECT_SLUG}}`）已完成 Bootstrap。

- Blueprint：`{{BLUEPRINT_ID}}` v{{BLUEPRINT_VERSION}}
- 架构：`{{ARCHITECTURE_STYLE}}` / `{{ARCHITECTURE_PATTERN}}`
- 主要平台：{{PLATFORM_NAME}}
- 包管理器：{{PACKAGE_MANAGER}}

请先阅读 `AGENTS.md`、`docs/PROJECT_PROFILE.md` 和 `docs/DESIGN.md`，再开始修改项目代码。

## 运行与冒烟验证（必须完成）

按 README 执行 `{{PROJECT_INSTALL_COMMAND}}` → typecheck → build，启动应用后逐项验证以下 URL 可访问，并把结果写进完成总结：

| 应用 | URL | 期望 |
|---|---|---|
| 前台 / 后台 / API | `http://127.0.0.1:<port>/` 与 `/health` | HTTP 2xx/3xx |

> 多应用单仓默认端口：HR 前台 3000、运营后台 3002、API 3100（以实际生成的 README 为准）。
> 推荐用 `python3 <skill-dir>/scripts/smoke.py --dir <project-dir>` 自动检查，并附上输出。

## 下一步建议

1. 阅读 `AGENTS.md` 了解 Agent 分工与权限。
2. 从 `docs/00-research/stack-decision.md` 与 `design-token-spec.md` 开始设计迭代。
3. 用 Codex 打开项目后，基于 mock-first 基线开发真实 API 与页面。
