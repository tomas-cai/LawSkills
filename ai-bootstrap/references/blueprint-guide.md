# AI Bootstrap Blueprint Guide

## 最小规范

每个 Blueprint 使用一个 YAML 文件，至少包含：

```yaml
id: unique-id
name: Human Readable Name
version: 1.0.0
description: Short description
tags: [language, framework]

stack:
  frontend:
    framework: none
    language: none
  backend:
    framework: required-framework
    language: required-language
  database:
    primary: postgres
    version: "16"

architecture:
  style: layered
  pattern: modular-monolith

design_system:
  status: required
  ui_library: shadcn
  styling: tailwind-css
  icon_library: lucide-react
  color_mode: light-dark
  theme_entry:
    framework: src/main.tsx
    global_tokens: src/index.css
    components: component variants and theme provider
  component_baseline: [button, input, card, badge, navigation, dialog, table/list, empty/error]

layout:
  source_root: src/
  key_dirs:
    src/: "前端源码"
  conventions: "遵循对应技术栈官方目录约定，不自行发明结构"

commands:
  install: "pnpm install"
  dev: "pnpm dev"
  test: "pnpm test"

skills:
  - name: "Nuxt UI"
    description: "官方 Nuxt UI 使用技能"
    install: "npx skills add nuxt/ui"
    trigger: "/nuxt-ui"
    docs: "https://ui.nuxtjs.org.cn/docs/getting-started/ai/skills"
```

## 约束

- 使用语义化版本号。
- 数据库使用 `stack.database.primary` 表示主数据库，版本放在 `stack.database.version` 或主数据库对象中。
- 所有值必须能被 AI Bootstrap 的依赖无关 YAML 子集解析。
- 新 Blueprint 至少需要一个生成与验证回归测试。
- 包含前端时必须声明 `design_system`：UI 库、样式方案、图标、主题入口和组件基线；这些字段用于生成 `docs/00-research/design-token-spec.md`。
- `design_system` 只声明实现能力和入口，不把 UI 库默认主题当作产品设计；颜色和版式由生成的语义令牌规范进一步确认。
- 必须声明 `layout`：`source_root` 与 `key_dirs` 要符合技术栈官方约定，不要自创目录名；官方未规定子目录时，采用该生态常见模块边界并在 `conventions` 中说明。
- 建议声明 `commands`：从项目根目录可直接运行的安装、启动和测试命令，避免生成 README 时给不同技术栈套用同一个 `pnpm install`。
- 可选声明 `skills`：当技术栈提供官方 AI Skill 时，记录名称、安装命令、触发词和官方文档；生成器会写入 `AGENTS.md`、`README.md` 和 `PROJECT_PROFILE.md`。
- 后端框架使用独立 npm 包名时，应在 `stack.backend.package` 声明真实包名；例如独立 Nitro API 使用 `nitropack`，而不是旧版 `nitro` 包。
- 不要在 Blueprint 中放入凭据、环境变量值或不可移植的绝对路径。

## 目录结构契约

- 顶层治理结构（`AGENTS.md`、`docs/`、`.ai-bootstrap/`）在所有 Blueprint 间保持统一。
- 应用源码目录按每个 Blueprint 的 `layout` 声明，生成器会把目录表写入 `README.md`、`DESIGN.md` 和 `PROJECT_PROFILE.md`。
- 新项目按官方约定生成骨架；现有项目不强制重构，`detect.py` 记录实际结构，AI 按现状工作。
- 多应用项目每个 app 独立声明 `layout`，不共用一套源码结构。

## 多应用与独立 design_system

一个 Blueprint 的 `stack.frontend` 和 `design_system` 描述主前端应用。当产品包含多个独立前端应用（例如 PC 管理端 + uni-app 移动端）时，不要把不同应用的 UI 库、样式方案和主题入口强行合并成一个 `design_system`：

- 每个应用独立选择 UI 库、样式库、图标库和主题入口。
- 产品级语义令牌可以共享，但实现入口按应用分别声明。
- 移动端默认推荐 uni-app + Vue3 + uni-ui；它与现有后端 Blueprint 组合，而不是复用 PC 前端方案。
- `docs/00-research/stack-decision.md` 必须记录每个应用的完整组合。
- `docs/00-research/design-token-spec.md` 必须按应用记录主题入口、组件基线和验收标准。

当前生成器以主应用为生成目标；多应用组合由 Codex 在生成后按 `references/design-token-guide.md` 补写，并纳入最终验证检查。

## 可选：基础功能基线 starter

Blueprint 可声明 `starter`，在全新项目生成时复制 `templates/starter/` 下的 mock-first 基础功能（如 JWT + author 鉴权、项目新建/编辑）。多应用单仓使用 `template_dirs`（复制根 + 各 `apps/<id>/` 目录）；`generate.py` 会把实际落地状态写入 manifest：

```yaml
starter:
  enabled: true
  mode: mock-first
  template_dirs:
    - dir: nuxt-monorepo-root
      target: ""
    - dir: nuxt-app-hr
      target: apps/app-web-hr
    - dir: nuxt-app-platform
      target: apps/app-web-platform
    - dir: nitro-server-standalone
      target: apps/app-web-server
  features:
    - jwt-author-auth
    - project-create-edit
```

- `enabled` 控制默认是否复制；`--no-starter` / `--starter` 可在 CLI 覆盖。
- `template_dirs` 每个 `{dir, target}` 指向 `templates/starter/<dir>/`；`.vue/.ts/.tsx/.js/.jsx/.json/.md/.yaml/.css` 等文本文件复制时渲染 `{{VARIABLE}}`（如 `{{PROJECT_NAME}}`、`{{PROJECT_SLUG}}`）。
- manifest 的 `starter.status` 如实记录落地状态（`applied` / `partial` / `missing` / `skipped`），并列出 `applied_dirs` / `missing_dirs`；不要把未复制成功的模板目录记为「已生成」。
- 新 Blueprint 若声明 starter，必须同时补充生成与验证回归测试。

## 验证

```bash
python3 scripts/generate.py --dir /tmp/example --blueprint <id> --dry-run
python3 scripts/validate.py --dir /tmp/example
```
