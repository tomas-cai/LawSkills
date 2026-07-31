---
name: project-scaffold
description: >
  Use when "start new project", "init project", "scaffold",
  "create project structure", "setup documentation governance",
  or "add docs structure" is mentioned. Also use when reorganizing
  an existing project's governance documentation.
---

# project-scaffold — 项目文档治理初始化

## 核心能力

一键生成以下结构：

```
project/
├─ AGENTS.md             路由层 + 令牌矩阵 + 路由表
├─ docs/
│  ├─ DESIGN.md          品牌共享规范
│  ├─ 00-research/       调研
│  ├─ 01-requirements/   需求
│  ├─ 02-specs/          设计规格
│  ├─ 03-plans/          实施计划
│  ├─ 04-reviews/        审查
│  ├─ 05-verification/   验证
│  ├─ 06-decisions/      决策记录
│  └─ design/
│     └─ {app}-design.md 每个应用一份
├─ .gitignore
└─ packages/
   └─ design-tokens/     设计令牌包（Monorepo）
```

## 使用方法

调用 scaffold.py 脚本，传入项目参数：

```bash
python3 <skill-dir>/scripts/scaffold.py \
  --dir /path/to/project \
  --name "MyProject" \
  --description "项目描述" \
  --type monorepo \
  --apps '...' \
  --primary "#00C8A1"
```

### 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `--dir` | 是 | 目标项目根目录 |
| `--name` | 否 | 项目名称（默认用目录名） |
| `--description` | 否 | 品牌描述，写入 DESIGN.md |
| `--type` | 否 | `monorepo` 或 `single` |
| `--apps` | 是 | JSON 数组，每项含 `dir`、`desc`、`framework` |
| `--primary` | 否 | 主色 hex |
| `--platform` | 否 | AI 平台标识（trae / codex / cursor），控制 AGENTS.md 中的技能路径 |
| `--dry-run` | 否 | 预览模式，只打印文件列表不写入 |

### 支持的 framework

| 值 | 模板 | 生成的规范 |
|-----|------|-----------|
| `nuxt` / 默认 | `app-nuxt.md` | Tailwind + Nuxt UI + motion-v + Lucide |
| `next` / `next.js` | `app-next.md` | Tailwind + shadcn/ui + framer-motion + Lucide |
| `uni-app` / `mobile` | `app-mobile.md` | nutui-uniapp + uni-app 原生动画 |

## 模板文件体系

所有模板在 `templates/` 目录下，使用 `{{KEY}}` 占位符替换：

| 模板文件 | 用途 | 适用场景 |
|---------|------|---------|
| `templates/AGENTS.md` | 路由层 + 令牌矩阵 + 优先级规则 | 所有项目 |
| `templates/DESIGN.md` | 品牌共享设计规范 | 所有项目 |
| `templates/app-nuxt.md` | Nuxt(UI 3) 应用设计规范 + motion-v | `framework: nuxt` |
| `templates/app-next.md` | Next.js 应用设计规范 + shadcn/ui | `framework: next / next.js` |
| `templates/app-mobile.md` | uni-app 移动端设计规范 + nutui | `framework: uni-app / uniapp / mobile` |

### 可用占位符

| 占位符 | 来源 | 说明 |
|--------|------|------|
| `{{PROJECT_NAME}}` | `--name` | 项目名 |
| `{{BRAND_DESCRIPTION}}` | `--description` | 品牌描述 |
| `{{APP_NAME}}` | apps 数组每项 `dir` | 应用标识 |
| `{{APPS_ROWS}}` | apps 数组 | AGENTS.md 应用路由表 |
| `{{COLOR_TABLE}}` | 令牌 + `--primary` | 颜色矩阵 markdown 表格 |
| `{{DEV_TABLE}}` | apps 数组 + type | 开发命令表 |
| `{{TOKEN_PRIMARY}}` 等 | 令牌默认值 / `--primary` | 颜色 hex |
| `{{PLATFORM_SKILLS_PATH}}` | `--platform` | AI 平台技能路径 |

## 输出物

1. **AGENTS.md** — 路由层 + 应用路由表 + 令牌矩阵 + 优先级规则
2. **docs/DESIGN.md** — 品牌共享规范
3. **docs/design/{app}-design.md** — 每应用框架规范
4. **docs/00-06/** — Superpowers 阶段目录
5. **packages/design-tokens/** （Monorepo 时生成）
6. **.gitignore** — 按项目类型生成的 Git 忽略规则
7. **README.md**

## 验证检查

- [ ] AGENTS.md 路由表列齐了所有 apps
- [ ] 每个 app 有对应的设计文档
- [ ] 令牌矩阵颜色值正确
- [ ] Monorepo 有 packages/design-tokens/ 骨架
- [ ] 单应用没有 packages 目录
- [ ] .gitignore 匹配项目类型
- [ ] dry-run 不产生实际写入
