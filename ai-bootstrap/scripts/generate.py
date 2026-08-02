#!/usr/bin/env python3
"""
AI Bootstrap — Governance File Generator v1.3

Generates governance files (AGENTS.md, PROJECT_PROFILE.md, DESIGN.md, MEMORY.md, ADR, etc.)
based on a Blueprint definition and user input.

Usage:
    python3 generate.py --dir /path/to/project --blueprint next-fullstack
    python3 generate.py --dir /path/to/project --blueprint auto --name MyApp --dry-run
"""

import argparse
import json
import os
import subprocess
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from yaml_utils import dump_yaml, load_yaml
from framework_gate import constraints_for_ui_library, render_constraints_markdown
from layout import (
    ADR_DIR,
    ADR_INDEX_PATH,
    BACKLOG_PATH,
    CURRENT_TASKS_PATH,
    DECISION_INDEX_PATH,
    DESIGN_PATH,
    DESIGN_TOKEN_SPEC_PATH,
    INITIAL_ADR_PATH,
    MANIFEST_PATH,
    MEMORY_PATH,
    PHASE_READMES,
    PROJECT_PROFILE_PATH,
    REVIEW_INDEX_PATH,
)


# ─── Constants ────────────────────────────────────────────────────────────────

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = SKILL_DIR / "templates"
BLUEPRINTS_DIR = TEMPLATES_DIR / "blueprints"
GOV_TEMPLATES_DIR = TEMPLATES_DIR / "governance"
PROJECT_TEMPLATES_DIR = TEMPLATES_DIR / "project"
STARTER_TEMPLATES_DIR = TEMPLATES_DIR / "starter"

# Text files inside starter templates get {{VARIABLE}} rendering on copy.
STARTER_TEXT_EXTENSIONS = {
    ".vue", ".ts", ".js", ".mjs", ".cjs", ".json", ".md", ".markdown",
    ".yaml", ".yml", ".css", ".scss", ".html", ".txt", ".toml",
}
STARTER_TEXT_FILENAMES = {".env.example", ".gitignore"}

BOOTSTRAP_VERSION = "1.7.0"

# Agent platform configurations
AGENT_PLATFORMS = {
    "codex": {
        "name": "Codex",
        "color": "#10b981",
        "file": ".codex/instruction.md",
        "role": "lead-architect",
    },
    "claude-code": {
        "name": "Claude Code",
        "color": "#8b5cf6",
        "file": "CLAUDE.md",
        "role": "backend-engineer",
    },
    "cursor": {
        "name": "Cursor",
        "color": "#f59e0b",
        "file": ".cursorrules",
        "role": "frontend-engineer",
    },
    "trae": {
        "name": "Trae",
        "color": "#3b82f6",
        "file": ".trae/rules/",
        "role": "fullstack-engineer",
    },
    "windsurf": {
        "name": "Windsurf",
        "color": "#06b6d4",
        "file": ".windsurfrules",
        "role": "fullstack-engineer",
    },
    "gemini": {
        "name": "Gemini CLI",
        "color": "#4285f4",
        "file": ".gemini/config/",
        "role": "ai-engineer",
    },
}


# ─── Blueprint Registry ───────────────────────────────────────────────────────

def load_blueprint(blueprint_id: str) -> Optional[dict]:
    """Load a blueprint definition from the blueprints directory."""
    bp_file = BLUEPRINTS_DIR / f"{blueprint_id}.yaml"
    if bp_file.exists():
        # Simple YAML-like parser for now; could use pyyaml
        return _parse_blueprint_yaml(bp_file)
    return None


def _blueprint_ids() -> list[str]:
    return sorted(path.stem for path in BLUEPRINTS_DIR.glob("*.yaml"))


def _recommend_blueprint(detection: dict) -> Optional[str]:
    """Return the highest-confidence Blueprint for a detection result."""
    candidates: list[tuple[str, float]] = []
    for language in detection.get("project", {}).get("languages", []):
        name = language.get("name", "").lower()
        frameworks = {key.lower() for key in language.get("frameworks", {}).keys()}
        if name in {"typescript", "javascript"}:
            if "next" in frameworks:
                candidates.append(("next-fullstack", 0.95))
            if "react" in frameworks:
                candidates.append(("react-fastapi", 0.90))
            if "vue" in frameworks or "nuxt" in frameworks:
                candidates.append(("vue-django", 0.85))
            if "nestjs" in frameworks or "nest" in frameworks:
                candidates.append(("next-fullstack", 0.85))
        elif name == "python":
            if "django" in frameworks:
                candidates.append(("vue-django", 0.80))
            if "fastapi" in frameworks:
                candidates.append(("react-fastapi", 0.80))
                candidates.append(("python-ml-service", 0.75))
        elif name == "go":
            candidates.append(("go-microservice", 0.90))
        elif name == "rust":
            candidates.append(("rust-axum-api", 0.90))

    if candidates:
        candidates.sort(key=lambda item: -item[1])
        return candidates[0][0]
    if detection.get("is_empty", False):
        return "next-fullstack"
    return None


def resolve_auto_blueprint(project_path: Path) -> Optional[str]:
    """Resolve ``auto`` through the detection engine instead of a fake Blueprint."""
    detect_script = SKILL_DIR / "scripts" / "detect.py"
    try:
        result = subprocess.run(
            [sys.executable, str(detect_script), "--dir", str(project_path), "--deep", "--json"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        detection = json.loads(result.stdout)
        blueprint_id = _recommend_blueprint(detection)
        if blueprint_id:
            return blueprint_id
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        pass
    return None


def _parse_blueprint_yaml(filepath: Path) -> Optional[dict]:
    """Parse a Blueprint using the dependency-free YAML subset."""
    try:
        blueprint = load_yaml(filepath)
    except Exception:
        return None
    if not isinstance(blueprint, dict):
        return None
    blueprint.setdefault("id", filepath.stem)
    blueprint.setdefault("tags", [])
    blueprint.setdefault("stack", {})
    blueprint.setdefault("architecture", {})
    return blueprint


# ─── Template Engine ──────────────────────────────────────────────────────────

def render_template(template_path: Path, variables: dict) -> str:
    """Render a template with variable substitution."""
    try:
        content = template_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"<!-- Template not found: {template_path.name} -->"

    # Simple {{VARIABLE}} replacement
    for key, value in variables.items():
        placeholder = "{{" + key + "}}"
        if value is not None:
            content = content.replace(placeholder, str(value))

    # Templates intentionally use only flat variables.  Structured blocks are
    # rendered before this function (for example, AGENT_DEFINITIONS).
    # Only uppercase {{VARIABLE}} placeholders count as unresolved template
    # syntax; Vue/Nuxt {{ interpolation }} (lowercase expressions) is kept.
    import re
    unresolved = re.findall(r"\{\{\s*[A-Z][A-Z0-9_]*\s*\}\}|\{%", content)
    if unresolved:
        raise ValueError(f"Unsupported template syntax remains in {template_path.name}")

    return content


# ─── Variables Builder ────────────────────────────────────────────────────────

def _agent_definitions(agent_configs: list[dict]) -> str:
    blocks = []
    for config in agent_configs:
        blocks.append(
            "\n".join([
                f"### [{config['name']}](id: `{config['id']}`)",
                "",
                "| 属性 | 值 |",
                "|------|------|",
                f"| **ID** | `{config['id']}` |",
                f"| **角色** | {config['role']} |",
                f"| **颜色** | `{config['color']}` |",
                f"| **配置文件** | `{config['file']}` |",
                "",
                "**permissions**:",
                "- `read_all: true`",
                "- `write_files: role-scoped`",
                "- `write_gov: false` unless explicitly approved",
                f"- `write_adr: {'true' if config['role'] == 'lead-architect' else 'false'}`",
                "",
                "**constraints**:",
                "- Architecture changes require an ADR.",
                "- Read the Context Router before editing project files.",
            ])
        )
    return "\n\n".join(blocks)


def _architecture_constraints(style: str) -> str:
    normalized = (style or "").lower().replace("_", "-")
    if normalized in {"ddd", "domain-driven-design", "domain-driven"}:
        return "\n".join([
            "- **Domain 层纯业务**: 不引用框架、ORM 或外部库。",
            "- **Repository 模式**: Domain 定义接口，Infrastructure 负责实现。",
            "- **依赖倒置**: 外层依赖内层，Domain 不依赖 Infrastructure。",
            "- **聚合根**: 通过聚合根访问实体，禁止直接操作子实体。",
        ])
    if normalized == "clean":
        return "\n".join([
            "- **依赖规则**: 依赖方向从外向内，内层不依赖外层。",
            "- **接口适配器**: 外部依赖必须通过接口适配器访问。",
            "- **用例驱动**: Application 层定义用例并编排业务流程。",
        ])
    return "\n".join([
        "- **分层依赖**: 上层可以依赖下层，下层不能依赖上层。",
        "- **接口隔离**: 每层定义清晰的接口边界。",
    ])


def _primary_language(stack: dict) -> str:
    frontend = stack.get("frontend", {}) if isinstance(stack, dict) else {}
    backend = stack.get("backend", {}) if isinstance(stack, dict) else {}
    frontend_language = frontend.get("language") if isinstance(frontend, dict) else None
    backend_language = backend.get("language") if isinstance(backend, dict) else None
    return frontend_language if frontend_language and frontend_language != "none" else (backend_language or "unknown")


def _design_principles_yaml(style: str) -> str:
    normalized = (style or "").lower().replace("_", "-")
    principles = {
        "ddd": [
            "Domain 层不依赖框架、ORM 或外部服务",
            "聚合边界和业务不变量由 Domain 层维护",
            "外部能力通过端口与适配器接入",
        ],
        "clean": [
            "依赖方向从外向内，核心用例不依赖交付或基础设施细节",
            "外部服务和数据访问通过接口适配",
            "用例层负责业务流程编排",
        ],
    }.get(normalized, [
        "模块边界清晰，避免跨层反向依赖",
        "对外接口和数据模型保持明确、可测试",
        "基础设施细节与业务逻辑隔离",
    ])
    return "\n".join(f"    - {json.dumps(item, ensure_ascii=False)}" for item in principles)


def _coding_convention_yaml(language: str) -> str:
    conventions = {
        "python": ("snake_case", "PascalCase", "snake_case", "UPPER_SNAKE_CASE", 88),
        "go": ("snake_case", "PascalCase (exported)", "camelCase (unexported)", "CamelCase / UPPER_SNAKE_CASE", 100),
        "rust": ("snake_case", "PascalCase", "snake_case", "SCREAMING_SNAKE_CASE", 100),
        "typescript": ("kebab-case", "PascalCase", "camelCase", "UPPER_SNAKE_CASE", 100),
        "javascript": ("kebab-case", "PascalCase", "camelCase", "UPPER_SNAKE_CASE", 100),
    }
    files, classes, functions, constants, line_length = conventions.get(
        language.lower(), ("kebab-case", "PascalCase", "camelCase", "UPPER_SNAKE_CASE", 100)
    )
    return "\n".join([
        "    naming:",
        f"      files: {json.dumps(files, ensure_ascii=False)}",
        f"      classes: {json.dumps(classes, ensure_ascii=False)}",
        f"      functions: {json.dumps(functions, ensure_ascii=False)}",
        f"      constants: {json.dumps(constants, ensure_ascii=False)}",
        "    imports:",
        '      order: "standard-library→third-party→project-local"',
        f"    max_line_length: {line_length}",
    ])


def _architecture_boundaries(style: str) -> str:
    normalized = (style or "").lower().replace("_", "-")
    if normalized == "ddd":
        return "\n".join([
            "- **Domain**：业务规则、聚合与领域接口；不依赖框架。",
            "- **Application**：用例编排与事务边界。",
            "- **Infrastructure / Delivery**：数据库、消息、HTTP 与其他外部适配器。",
        ])
    if normalized == "clean":
        return "\n".join([
            "- **Core**：实体、用例和端口，保持独立可测试。",
            "- **Adapters**：HTTP、gRPC、持久化和消息适配器。",
            "- **Composition**：在入口处完成依赖装配。",
        ])
    return "\n".join([
        "- **Interface**：HTTP、CLI、事件或其他对外协议。",
        "- **Application**：业务流程与服务编排。",
        "- **Infrastructure**：持久化、缓存、队列和外部服务实现。",
    ])


def _engineering_practices(stack: dict, primary_language: str) -> str:
    backend = stack.get("backend", {}) if isinstance(stack, dict) else {}
    database = stack.get("database", {}) if isinstance(stack, dict) else {}
    ml = stack.get("ml", {}) if isinstance(stack, dict) else {}
    framework = backend.get("framework", "backend") if isinstance(backend, dict) else "backend"
    database_type = database.get("primary", "database") if isinstance(database, dict) else "database"
    practices = [
        f"- 使用 {framework} 的官方测试工具覆盖核心行为和错误路径。",
        f"- 为 {database_type} 访问定义清晰的数据边界、迁移策略与失败处理。",
        "- 在接口变更时同步更新规格、验证证据和决策记录。",
    ]
    if primary_language.lower() == "go":
        practices.append("- 在并发与网络调用中传播 context，并处理超时和取消。")
    elif primary_language.lower() == "python":
        practices.append("- 使用类型标注、格式化与静态检查保持 Python 服务边界清晰。")
    elif primary_language.lower() == "rust":
        practices.append("- 显式建模错误与所有权边界，避免不必要的 panic。")
    if isinstance(ml, dict) and ml.get("framework"):
        practices.append("- 记录模型、数据、实验与部署版本，确保推理结果可追溯。")
    return "\n".join(practices)



def _framework_constraints_markdown(stack: dict) -> str:
    """按 Blueprint 声明的 UI 库渲染 DESIGN.md「框架约束」段落。"""
    frontend = stack.get("frontend", {}) if isinstance(stack, dict) else {}
    ui_library = frontend.get("ui_library", "") if isinstance(frontend, dict) else ""
    constraints = constraints_for_ui_library(ui_library)
    return render_constraints_markdown(constraints)


def _design_token_spec(blueprint: dict, variables: dict) -> str:
    """Build the stack-aware design-token contract persisted with the project."""
    stack = blueprint.get("stack", {}) if isinstance(blueprint, dict) else {}
    frontend = stack.get("frontend", {}) if isinstance(stack, dict) else {}
    design = blueprint.get("design_system", {}) if isinstance(blueprint, dict) else {}
    framework = frontend.get("framework", "none")
    version = frontend.get("version", "")
    ui_library = frontend.get("ui_library", design.get("ui_library", "none"))
    required = framework not in (None, "", "none")
    status = design.get("status", "required" if required else "not-applicable")

    presets = {
        "nuxt-ui": {
            "direction": "calm command center: cool canvas, indigo action color, teal progress accent",
            "primary": "#4F46E5",
            "accent": "#0F9F9A",
        },
        "shadcn": {
            "direction": "quiet product surface: neutral canvas, ink-led hierarchy, one confident indigo action",
            "primary": "#4F46E5",
            "accent": "#0EA5E9",
        },
        "naive-ui": {
            "direction": "structured operations desk: slate surfaces, blue action color, amber attention state",
            "primary": "#2563EB",
            "accent": "#D97706",
        },
        "vant": {
            "direction": "mobile-first utility surface: light canvas, indigo action color, teal progress accent, 8px-friendly radii",
            "primary": "#4F46E5",
            "accent": "#0F9F9A",
        },
    }
    _library = str(ui_library).lower()
    preset = next(
        (v for k, v in presets.items() if k in _library),
        {
            "direction": "semantic product baseline; derive the accent from the product domain before implementation",
            "primary": "#2563EB",
            "accent": "#0EA5E9",
        },
    )
    preset_name = design.get("token_preset", ui_library or "framework-neutral")
    direction = design.get("direction", preset["direction"])
    primary = design.get("primary", preset["primary"])
    accent = design.get("accent", preset["accent"])
    theme_entry = design.get("theme_entry", {})
    if not isinstance(theme_entry, dict):
        theme_entry = {"implementation": str(theme_entry)}
    component_baseline = design.get("component_baseline", [
        "button", "input", "card", "badge", "navigation", "dialog", "table/list", "empty/error",
    ])
    if not isinstance(component_baseline, list):
        component_baseline = [str(component_baseline)]

    lines = [
        "# Design Token Spec",
        "",
        "> 这是 Bootstrap 的产品设计基线，不是 UI 库默认主题的复制品。实现前需核对当前安装版本的官方主题 API，并保持语义令牌为唯一来源。",
        "",
        "## 1. 选型上下文",
        "",
        f"- **项目**: {variables.get('PROJECT_NAME', '')}",
        f"- **前端**: {framework} {version}".rstrip(),
        f"- **UI 库**: {ui_library}",
        f"- **令牌状态**: {status}",
        f"- **令牌基线**: {preset_name}",
        f"- **设计方向**: {direction}",
        "",
    ]
    if not required:
        lines.extend([
            "该 Blueprint 不包含前端界面，因此本文件只作为占位记录；新增前端时必须重新选择 UI 库、主题入口和令牌实现方式。",
            "",
        ])
        return "\n".join(lines)

    lines.extend([
        "## 2. 技术栈主题入口",
        "",
        "| 层次 | 入口 | 约束 |",
        "|---|---|---|",
        f"| 框架主题 | {theme_entry.get('framework', '框架官方 theme/config')} | 优先使用框架官方主题入口 |",
        f"| 全局令牌 | {theme_entry.get('global_tokens', '全局 CSS variables')} | 语义变量集中定义，页面禁止散落魔法值 |",
        f"| 组件主题 | {theme_entry.get('components', '组件库 theme/variants')} | 通过组件库 variants/slots 复用 |",
        f"| 图标 | {design.get('icon_library', '使用项目已选图标库')} | 统一尺寸、笔画和语义，不混用 emoji |",
        "",
        "## 3. 语义颜色",
        "",
        "| 令牌 | Light 基线 | 用途 |",
        "|---|---|---|",
        "| `canvas` | `#F6F8FC` | 页面底色 |",
        "| `surface` | `#FFFFFF` | 卡片、表单、导航面板 |",
        "| `surface-muted` | `#EEF2F7` | 次级区块和禁用背景 |",
        "| `ink` | `#172033` | 主文本和标题 |",
        "| `ink-muted` | `#667085` | 辅助文本、说明 |",
        "| `border` | `#D8DEE9` | 分隔线和控件边界 |",
        f"| `primary` | `{primary}` | 主操作、链接、选中态 |",
        f"| `accent` | `{accent}` | 产品特征、进度或辅助强调 |",
        "| `success` | `#15803D` | 成功状态 |",
        "| `warning` | `#B45309` | 警告和需处理状态 |",
        "| `danger` | `#B42318` | 错误、破坏性操作 |",
        "| `focus` | `#7C3AED` | 键盘焦点环 |",
        "",
        "Dark mode 必须重新检查对比度，不能只对 Light 值做反转；状态色在 dark surface 上至少保持可读性。",
        "",
        "## 4. Typography scale",
        "",
        "| 角色 | 字号 / 行高 | 字重 |",
        "|---|---|---|",
        "| Display | 40/48 | 700 |",
        "| Heading | 28/36 | 650 |",
        "| Body | 16/24 | 400 |",
        "| Label | 13/18 | 600 |",
        "| Caption | 12/16 | 500 |",
        "| Data/code | 13/20 | 500 |",
        "",
        "字体优先使用产品允许的 web font；未加载成功时回退到 `Inter`, `PingFang SC`, `Microsoft YaHei`, `sans-serif`。标题、正文、标签和数据不得共用未定义的默认字号。",
        "",
        "## 5. Layout、shape 与行为",
        "",
        "- **Spacing**: `4, 8, 12, 16, 24, 32, 48, 64` px；页面区块优先使用 24/32/48 的节奏。",
        "- **Content width**: reading `720px`，workbench `1200px`，wide dashboard `1440px`；不要让首屏内容无限拉伸。",
        "- **Control height**: compact `32px`，default `40px`，large `48px`；同一表单区只选一种密度。",
        "- **Radius**: control `8px`，card `12px`，overlay `16px`；不要每个组件自行发明圆角。",
        "- **Border / shadow**: 默认使用 1px border；shadow 只表达层级，不作为装饰背景。",
        "- **Breakpoints**: `640 / 768 / 1024 / 1280px`；移动端先保证操作顺序和触控目标，再压缩布局。",
        "- **Motion**: 过渡 150–200ms，页面级进入动效不超过一次；尊重 `prefers-reduced-motion`。",
        "- **Focus**: 所有可交互元素必须有 2px focus ring，不能仅依赖颜色变化。",
        "",
        "## 6. 组件基线",
        "",
    ])
    for component in component_baseline:
        lines.append(f"- [ ] `{component}`：定义 default / hover / pressed / selected / disabled / loading（适用时）状态，并验证键盘焦点与响应式表现。")
    lines.extend([
        "",
        "## 7. 实现规则",
        "",
        f"1. 在 `{theme_entry.get('global_tokens', '全局主题文件')}` 建立语义变量，再映射到 `{ui_library}` 的 theme、slots 或 variants。",
        "2. 页面和业务组件只能消费语义令牌（如 `primary`, `surface`, `ink-muted`），禁止直接复制 hex、任意 Tailwind 色阶或 UI 库默认色。",
        "3. 首屏完成前，至少验收一个真实空状态、一个错误状态、一个表单控件和一个主操作，不以“组件能渲染”作为完成标准。",
        "4. 若产品领域需要更强识别度，优先调整 `accent`、字体和内容结构；不要用渐变、阴影和装饰堆砌来弥补没有设计方向。",
        "",
        "## 8. 首屏验收清单",
        "",
        "- [ ] 首屏能看出产品的单一核心任务，而不是 UI 库 starter demo。",
        "- [ ] 颜色、字号、间距、圆角、控件密度均来自本文件。",
        "- [ ] Light / dark（如支持）、hover、focus、disabled、loading、empty、error 状态已验证。",
        "- [ ] 640px 及以上断点和移动端触控目标可用。",
        "- [ ] 运行官方组件库主题检查，确认本文件的实现入口与安装版本一致。",
    ])
    return "\n".join(lines)


def _project_layout_table(blueprint: dict) -> str:
    """Render the Blueprint-declared stack layout as a Markdown table."""
    layout = blueprint.get("layout", {}) if isinstance(blueprint, dict) else {}
    key_dirs = layout.get("key_dirs", {}) if isinstance(layout, dict) else {}
    if not isinstance(key_dirs, dict) or not key_dirs:
        key_dirs = {"src/": "application source code (default layout)"}

    rows = ["| 目录 | 职责 |", "|---|---|"]
    source_root = layout.get("source_root") if isinstance(layout, dict) else None
    if source_root and source_root not in key_dirs:
        rows.append(f"| `{source_root}` | 源码根目录 |")
    for path, description in key_dirs.items():
        rows.append(f"| `{path}` | {description} |")
    return "\n".join(rows)


def _project_layout_conventions(blueprint: dict) -> str:
    """Return the stack-specific layout convention declared by the Blueprint."""
    layout = blueprint.get("layout", {}) if isinstance(blueprint, dict) else {}
    if isinstance(layout, dict) and layout.get("conventions"):
        return str(layout["conventions"])
    return "目录结构遵循对应技术栈的官方约定；官方未约定的子目录按业务模块补充，并记录在本文件中。"


def _recommended_skills_section(blueprint: dict) -> str:
    """Render the Blueprint-declared recommended AI skills as a Markdown section."""
    skills = blueprint.get("skills", []) if isinstance(blueprint, dict) else []
    if not isinstance(skills, list) or not skills:
        return ""

    lines = [
        "## 推荐 AI 技能",
        "",
        "| 技能 | 说明 | 安装命令 | 调用方式 | 官方文档 |",
        "|---|---|---|---|---|",
    ]
    for skill in skills:
        if not isinstance(skill, dict):
            continue
        name = skill.get("name", "Skill")
        description = skill.get("description", "")
        install = skill.get("install", "")
        trigger = skill.get("trigger", "")
        docs = skill.get("docs", "")
        lines.append(f"| {name} | {description} | `{install}` | `{trigger}` | [文档]({docs}) |")
    return "\n".join(lines) + "\n"


def _agents_yaml(agent_configs: list[dict]) -> str:
    lines = []
    for config in agent_configs:
        lines.extend([
            f"      - id: {json.dumps(config['id'], ensure_ascii=False)}",
            f"        role: {json.dumps(config['role'], ensure_ascii=False)}",
        ])
    return "\n".join(lines)


def _agent_summary_rows(agent_configs: list[dict]) -> str:
    return "\n".join(f"| {config['name']} | {config['role']} |" for config in agent_configs)


def _slugify(name: str) -> str:
    """Convert a project name into a package-safe slug."""
    import re
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower()).strip("-")
    return slug or "app"


def build_variables(args, blueprint: dict) -> dict:
    """Build template variables from args and blueprint."""
    now = datetime.now()
    project_id = f"proj-{uuid.uuid4().hex[:8]}"

    # Resolve agent list
    requested_agent_ids = [a.strip() for a in args.agents.split(",")] if args.agents else ["codex", "cursor"]
    agent_ids = [aid for aid in requested_agent_ids if aid in AGENT_PLATFORMS]
    if not agent_ids:
        agent_ids = ["codex", "cursor"]
    agent_configs = []
    for aid in agent_ids:
        config = dict(AGENT_PLATFORMS[aid])
        config["id"] = aid
        agent_configs.append(config)

    # Resolve platform
    platform = args.platform or agent_ids[0] if agent_ids else "codex"
    platform_config = AGENT_PLATFORMS.get(platform, AGENT_PLATFORMS["codex"])

    # Determine if this is a new project or existing
    project_dir = Path(args.dir).resolve()
    is_empty = not any(project_dir.iterdir()) if project_dir.exists() else True

    # Package manager detection
    pm = blueprint.get("stack", {}).get("package_manager", {})
    if isinstance(pm, str):
        pm_name = pm
    elif isinstance(pm, dict):
        pm_name = pm.get("name", "npm")
    else:
        pm_name = "npm"

    stack = blueprint.get("stack", {})
    frontend_stack = stack.get("frontend", {}) if isinstance(stack, dict) else {}
    backend_stack = stack.get("backend", {}) if isinstance(stack, dict) else {}
    ai_stack = stack.get("ai", {}) if isinstance(stack, dict) else {}
    database = stack.get("database", {}) if isinstance(stack, dict) else {}
    deployment_stack = stack.get("deployment", {}) if isinstance(stack, dict) else {}
    primary_database = database.get("primary", {}) if isinstance(database, dict) else {}
    if isinstance(primary_database, dict):
        database_type = primary_database.get("type") or primary_database.get("name", "unknown")
        database_version = primary_database.get("version") or database.get("version", "")
    else:
        database_type = primary_database or database.get("type", "unknown")
        database_version = database.get("version", "")
    architecture_style = blueprint.get("architecture", {}).get("style", "layered")
    primary_language = _primary_language(stack)

    return {
        "PROJECT_ID": project_id,
        "PROJECT_NAME": args.name or project_dir.name,
        "PROJECT_SLUG": _slugify(args.name or project_dir.name),
        "PROJECT_DESCRIPTION": args.description or "AI Native Project",
        "PROJECT_VERSION": "1.0.0",
        "CREATED_DATE": now.strftime("%Y-%m-%d"),
        "CREATED_TIMESTAMP": now.isoformat(),
        "BOOTSTRAP_VERSION": BOOTSTRAP_VERSION,
        "PLATFORM": platform,
        "PLATFORM_NAME": platform_config["name"],
        "PLATFORM_FILE": platform_config["file"],
        "PLATFORM_ROLE": platform_config["role"],
        "PLATFORM_COLOR": platform_config["color"],

        # Blueprint info
        "BLUEPRINT_ID": blueprint.get("id", "custom"),
        "BLUEPRINT_NAME": blueprint.get("name", "Custom Project"),
        "BLUEPRINT_VERSION": blueprint.get("version", "1.0.0"),
        "BLUEPRINT_TAGS": ", ".join(str(tag) for tag in blueprint.get("tags", [])),

        # Stack info
        "FRONTEND_FRAMEWORK": frontend_stack.get("framework", "unknown"),
        "FRONTEND_VERSION": frontend_stack.get("version", "latest"),
        "FRONTEND_LANGUAGE": frontend_stack.get("language", "unknown"),
        "FRONTEND_UI_LIBRARY": frontend_stack.get("ui_library", "none"),
        "FRONTEND_STATE_MANAGEMENT": frontend_stack.get("state_management", "none"),
        "PRIMARY_LANGUAGE": primary_language,
        "BACKEND_FRAMEWORK": backend_stack.get("framework", "unknown"),
        "BACKEND_VERSION": backend_stack.get("version", "latest"),
        "BACKEND_LANGUAGE": backend_stack.get("language", "unknown"),
        "BACKEND_API_STYLE": backend_stack.get("api_style", "unknown"),
        "DATABASE_TYPE": database_type,
        "DATABASE_VERSION": database_version,
        "DATABASE_PRODUCTION": database.get("production", "none"),
        "ORM": backend_stack.get("orm", "none"),
        "AI_SDK": ai_stack.get("sdk", "none"),
        "AUTH_PROVIDER": stack.get("auth", {}).get("provider", "none"),
        "DEPLOYMENT_TYPE": deployment_stack.get("type", "none"),
        "DEPLOYMENT_PLATFORM": deployment_stack.get("platform", "none"),
        "PACKAGE_MANAGER": pm_name,
        "MONOREPO_TOOL": stack.get("monorepo", "none"),
        "PROJECT_LAYOUT_TABLE": _project_layout_table(blueprint),
        "PROJECT_LAYOUT_CONVENTIONS": _project_layout_conventions(blueprint),
        "PROJECT_INSTALL_COMMAND": blueprint.get("commands", {}).get("install", "pnpm install"),
        "PROJECT_DEV_COMMAND": blueprint.get("commands", {}).get("dev", "pnpm dev"),
        "PROJECT_TEST_COMMAND": blueprint.get("commands", {}).get("test", "pnpm test"),
        "PROJECT_SKILLS_SECTION": _recommended_skills_section(blueprint),

        # Architecture
        "ARCHITECTURE_STYLE": architecture_style,
        "ARCHITECTURE_PATTERN": blueprint.get("architecture", {}).get("pattern", "modular-monolith"),

        # Agent configs
        "AGENT_LIST": agent_configs,
        "AGENT_DEFINITIONS": _agent_definitions(agent_configs),
        "ARCHITECTURE_CONSTRAINTS": _architecture_constraints(architecture_style),
        "AGENT_IDS_CSV": ",".join(agent_ids),
        "AGENT_COUNT": len(agent_configs),
        "AGENTS_YAML": _agents_yaml(agent_configs),
        "AGENT_SUMMARY_ROWS": _agent_summary_rows(agent_configs),
        "DESIGN_PRINCIPLES_YAML": _design_principles_yaml(architecture_style),
        "CODING_CONVENTION_YAML": _coding_convention_yaml(primary_language),
        "ARCHITECTURE_BOUNDARIES": _architecture_boundaries(architecture_style),
        "ENGINEERING_PRACTICES": _engineering_practices(stack, primary_language),
        "FRAMEWORK_CONSTRAINTS": _framework_constraints_markdown(stack),

        # Project state
        "IS_NEW_PROJECT": str(is_empty).lower(),
        "IS_EMPTY": str(is_empty).lower(),

        # Detection
        "DETECTION_CONFIDENCE": getattr(args, "detection_confidence", "0.0"),
    }


# ─── File Generator ──────────────────────────────────────────────────────────

def generate_file(
    template_name: str,
    output_path: Path,
    variables: dict,
    dry_run: bool = False,
    force: bool = False,
) -> Optional[Path]:
    """Generate a single file from a template."""
    template_file = template_name
    # If template_name is just a name, look in the templates directory
    if not template_name.startswith("/"):
        # Check governance templates first, then project templates
        candidate = GOV_TEMPLATES_DIR / template_name
        if candidate.exists():
            template_file = candidate
        else:
            candidate = PROJECT_TEMPLATES_DIR / template_name
            if candidate.exists():
                template_file = candidate
            else:
                # Check if the full path was given
                template_file = Path(template_name)
                if not template_file.exists():
                    print(f"  ⚠ Template not found: {template_name}")
                    return None

    rendered = render_template(Path(template_file), variables)

    if output_path.exists() and not force:
        print(f"  ⏭ Skipped existing file: {output_path}")
        return None

    if dry_run:
        print(f"  📄 Would create: {output_path}")
        return output_path

    # Create parent directories
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write file
    output_path.write_text(rendered, encoding="utf-8")
    print(f"  ✅ Created: {output_path.name}")
    return output_path


def generate_content_file(
    output_path: Path,
    content: str,
    dry_run: bool = False,
    force: bool = False,
) -> Optional[Path]:
    """Write a generated Markdown artifact while preserving existing files."""
    if output_path.exists() and not force:
        print(f"  ⏭ Skipped existing file: {output_path}")
        return None
    if dry_run:
        print(f"  📄 Would create: {output_path}")
        return output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    print(f"  ✅ Created: {output_path.relative_to(output_path.parents[1])}")
    return output_path


def _starter_dirs_from_blueprint(starter: dict) -> list[dict]:
    """Resolve the list of {dir, target} starter specs from a blueprint."""
    dirs = starter.get("template_dirs")
    if isinstance(dirs, list) and dirs:
        resolved = []
        for entry in dirs:
            if isinstance(entry, str) and entry:
                resolved.append({"dir": entry, "target": ""})
            elif isinstance(entry, dict) and entry.get("dir"):
                resolved.append({"dir": entry["dir"], "target": entry.get("target") or ""})
        if resolved:
            return resolved
    fallback = starter.get("template_dir") or "default"
    return [{"dir": fallback, "target": ""}]


def _copy_starter_directory(
    project_path: Path,
    template_dir: Path,
    target_rel: str,
    variables: dict,
    args,
    generated_files: list,
) -> tuple[int, int]:
    """Copy one starter directory into the project, rendering text templates."""
    created = 0
    skipped = 0
    for src in sorted(template_dir.rglob("*")):
        if src.is_dir():
            continue
        rel = src.relative_to(template_dir)
        dst = project_path / target_rel / rel
        if dst.exists() and not args.force:
            print(f"  ⏭ Skipped existing starter file: {target_rel}/{rel}")
            skipped += 1
            continue
        if args.dry_run:
            print(f"  📄 Would create starter file: {target_rel}/{rel}")
            created += 1
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix.lower() in STARTER_TEXT_EXTENSIONS or src.name in STARTER_TEXT_FILENAMES:
            rendered = render_template(src, variables)
            dst.write_text(rendered, encoding="utf-8")
        else:
            dst.write_bytes(src.read_bytes())
        print(f"  ✅ Created starter file: {target_rel}/{rel}")
        created += 1
        generated_files.append(str(dst))
    return created, skipped


def copy_starter_template(
    project_path: Path,
    blueprint: dict,
    args,
    generated_files: list,
    is_new: bool,
    variables: Optional[dict] = None,
) -> None:
    """Copy blueprint-declared starter baseline(s) into a new project.

    Supports both the legacy single ``template_dir`` and the new multi-app
    ``template_dirs`` list (each entry: {dir, target}), rendering text files
    with ``{{VARIABLE}}`` substitution so monorepo + app templates can share
    the project name/slug.
    """
    starter = blueprint.get("starter", {})
    if not isinstance(starter, dict):
        starter = {}

    enabled = bool(starter.get("enabled", False))
    if getattr(args, "starter", None) is True:
        enabled = True
    if getattr(args, "starter", None) is False:
        enabled = False

    if not enabled:
        print("  ⏭ Starter baseline skipped (not enabled for this blueprint)")
        return
    if not is_new:
        print("  ⏭ Starter baseline only applies to new projects")
        return

    specs = _starter_dirs_from_blueprint(starter)
    label = "multi-app monorepo" if len(specs) > 1 else specs[0]["dir"]
    print(f"  ── Basic Feature Starter ({label}) ──")

    total_created = 0
    total_skipped = 0
    for spec in specs:
        template_dir = STARTER_TEMPLATES_DIR / spec["dir"]
        if not template_dir.is_dir():
            print(f"  ⚠ Starter template directory not found: {template_dir}")
            continue
        created, skipped = _copy_starter_directory(
            project_path, template_dir, spec["target"], variables or {}, args, generated_files
        )
        total_created += created
        total_skipped += skipped

    if args.dry_run:
        print(f"  📋 Starter dry-run: {total_created} files would be copied.")
    else:
        print(f"  ✅ Starter baseline complete: {total_created} created, {total_skipped} skipped.")


def generate_manifest(
    args, blueprint: dict, generated_files: list, variables: dict, resolved_from: str
) -> dict:
    """Generate the bootstrap manifest."""
    starter = blueprint.get("starter", {})
    if not isinstance(starter, dict):
        starter = {}

    return {
        "manifest": {
            "bootstrap_version": BOOTSTRAP_VERSION,
            "generated_at": datetime.now().isoformat(),
            "generated_by": "AI Bootstrap Generator",
            "project": {
                "name": args.name or Path(args.dir).name,
                "dir": str(Path(args.dir).resolve()),
            },
            "blueprint": {
                "id": blueprint.get("id", "custom"),
                "version": blueprint.get("version", "1.0.0"),
                "resolved_from": resolved_from,
            },
            "starter": {
                "enabled": bool(starter.get("enabled", False)),
                "mode": starter.get("mode", "none"),
                "template_dir": starter.get("template_dir", "none"),
                "template_dirs": _starter_dirs_from_blueprint(starter),
                "features": starter.get("features", []),
            },
            "apps": blueprint.get("apps", []),
            "governance": {
                "files_generated": len(generated_files),
                "agents_configured": variables["AGENT_COUNT"],
                "adr_initialized": True,
                "context_router": "standard",
            },
            "validation": {
                "status": "pending",
                "timestamp": None,
            },
            "plugins": {
                "enabled": [],
            },
            "detection_summary": {
                "auto_detected": "0%",
                "wizard_input": "100%",
                "confidence": 0.0,
            },
        }
    }


# ─── Main Generation ─────────────────────────────────────────────────────────

def generate(args) -> list:
    """Run generation and return list of generated file paths."""
    project_path = Path(args.dir).resolve()

    if not project_path.exists():
        print(f"❌ Directory does not exist: {args.dir}", file=sys.stderr)
        sys.exit(1)

    is_new = not any(project_path.iterdir())
    force = getattr(args, "force", False)

    print(f"\n{'=' * 60}")
    print(f"  AI Bootstrap — Governance Generator v{BOOTSTRAP_VERSION}")
    print(f"{'=' * 60}")
    print(f"  Target:     {project_path}")
    print(f"  Blueprint:  {args.blueprint}")

    # Load blueprint, resolving auto from the detection engine when requested.
    resolved_blueprint_id = args.blueprint
    resolved_from = "user-selection"
    if args.blueprint == "auto":
        resolved_blueprint_id = resolve_auto_blueprint(project_path)
        if resolved_blueprint_id:
            resolved_from = "auto-detect"
            print(f"  Auto-resolved Blueprint: {resolved_blueprint_id}")
        else:
            resolved_from = "generic-fallback"
            print("  ⚠ Auto-detection found no matching Blueprint; using generic configuration")

    blueprint = load_blueprint(resolved_blueprint_id) if resolved_blueprint_id else None
    if not blueprint:
        blueprint_label = resolved_blueprint_id or args.blueprint
        print(f"  ⚠ Blueprint '{blueprint_label}' not found, using generic configuration")
        blueprint = {
            "id": blueprint_label,
            "name": blueprint_label.replace("-", " ").title(),
            "version": "1.0.0",
            "tags": ["custom"],
            "stack": {},
            "architecture": {},
        }

    print(f"  Project:    {args.name or project_path.name}")
    print(f"  Dry Run:    {'Yes' if args.dry_run else 'No'}")
    print()

    # Build variables
    variables = build_variables(args, blueprint)
    variables["IS_NEW_PROJECT"] = str(is_new).lower()
    variables["IS_EMPTY"] = str(is_new).lower()

    # Build output path
    out = project_path
    generated_files = []

    # ─── Generate Governance Files ───
    print("  ── Governance Files ──")

    # 1. AGENTS.md
    gen = generate_file("AGENTS.md", out / "AGENTS.md", variables, args.dry_run, force)
    if gen:
        generated_files.append(str(gen))

    # 2. Superpowers / SDD lifecycle structure.
    print("  ── SDD Lifecycle Documents ──")
    for phase_path, phase_content in PHASE_READMES.items():
        gen = generate_content_file(out / phase_path, phase_content, args.dry_run, force)
        if gen:
            generated_files.append(str(gen))

    # 3. Project DNA and design documents live under docs/.
    gen = generate_file("PROJECT_PROFILE.md", out / PROJECT_PROFILE_PATH, variables, args.dry_run, force)
    if gen:
        generated_files.append(str(gen))
    gen = generate_file("DESIGN.md", out / DESIGN_PATH, variables, args.dry_run, force)
    if gen:
        generated_files.append(str(gen))
    gen = generate_content_file(
        out / DESIGN_TOKEN_SPEC_PATH,
        _design_token_spec(blueprint, variables),
        args.dry_run,
        force,
    )
    if gen:
        generated_files.append(str(gen))
    gen = generate_file("MEMORY.md", out / MEMORY_PATH, variables, args.dry_run, force)
    if gen:
        generated_files.append(str(gen))

    # 4. ADRs and other decisions belong to the SDD decision phase.
    gen = generate_file("ADR-INDEX.md", out / ADR_INDEX_PATH, variables, args.dry_run, force)
    if gen:
        generated_files.append(str(gen))
    gen = generate_file("ADR-TEMPLATE.md", out / INITIAL_ADR_PATH, variables, args.dry_run, force)
    if gen:
        generated_files.append(str(gen))
    gen = generate_content_file(
        out / DECISION_INDEX_PATH,
        "# 决策日志\n\n> 记录非架构类、但需要长期追溯的项目决策。\n",
        args.dry_run,
        force,
    )
    if gen:
        generated_files.append(str(gen))

    # 5. Plans and reviews map directly to their Superpowers phases.
    tasks_current = f"""# 03 · Plans — 当前任务

## {args.name or project_path.name}

**Bootstrap 完成日期**: {variables['CREATED_DATE']}

### ⏳ 待办

- [ ] 启动开发环境
- [ ] 安装依赖
- [ ] 初始化数据库

### ✅ 已完成

- [x] AI Bootstrap 初始化完成
"""
    gen = generate_content_file(out / CURRENT_TASKS_PATH, tasks_current, args.dry_run, force)
    if gen:
        generated_files.append(str(gen))
    gen = generate_content_file(
        out / BACKLOG_PATH,
        "# 03 · Plans — Backlog\n\n> 暂无待规划事项。\n",
        args.dry_run,
        force,
    )
    if gen:
        generated_files.append(str(gen))
    gen = generate_content_file(
        out / REVIEW_INDEX_PATH,
        "# 04 · Reviews — 审查记录\n\n> 暂无审查记录。\n",
        args.dry_run,
        force,
    )
    if gen:
        generated_files.append(str(gen))

    # ─── Generate Project Files (for new projects only) ───
    if is_new:
        print()
        print("  ── Project Files (New Project) ──")
        gen = generate_file("README.md", out / "README.md", variables, args.dry_run, force)
        if gen:
            generated_files.append(str(gen))
        gen = generate_file(".gitignore", out / ".gitignore", variables, args.dry_run, force)
        if gen:
            generated_files.append(str(gen))

    # ─── Generate Basic Feature Starter (new projects only) ───
    copy_starter_template(project_path, blueprint, args, generated_files, is_new, variables)

    # ─── Generate Bootstrap Manifest ───
    manifest_path = out / MANIFEST_PATH
    manifest = generate_manifest(
        args, blueprint, generated_files + [str(manifest_path)], variables, resolved_from
    )
    manifest_will_write = force or not manifest_path.exists()
    if not args.dry_run and manifest_will_write:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(_dump_yaml(manifest), encoding="utf-8")
        print(f"  ✅ Created: bootstrap-manifest.yaml")
    elif args.dry_run and manifest_will_write:
        print(f"  📄 Would create: bootstrap-manifest.yaml")
    else:
        print(f"  ⏭ Skipped existing file: {manifest_path}")
    if manifest_will_write:
        generated_files.append(str(manifest_path))

    # ─── Summary ───
    print()
    if args.dry_run:
        print(f"  📋 Dry-run complete. {len(generated_files)} files would be generated.")
    else:
        print(f"  ✅ Generation complete. {len(generated_files)} files generated.")
    print()

    return generated_files


# ─── CLI Entry ────────────────────────────────────────────────────────────────


def _dump_yaml(data: dict, indent: int = 0) -> str:
    """Compatibility wrapper around the shared manifest serializer."""
    return dump_yaml(data, indent)


def main():
    parser = argparse.ArgumentParser(
        description="AI Bootstrap — Governance File Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 generate.py --dir ./my-project --blueprint next-fullstack --name MyApp --agents codex,cursor
  python3 generate.py --dir ./my-project --blueprint auto --description "My API" --dry-run
        """,
    )
    parser.add_argument("--dir", required=True, help="Target project directory")
    parser.add_argument("--name", help="Project name (default: directory name)")
    parser.add_argument("--blueprint", required=True, help="Blueprint ID (next-fullstack, react-fastapi, auto, etc.)")
    parser.add_argument("--description", help="Project description")
    parser.add_argument("--agents", default="codex,cursor", help="Agent platforms (comma-separated)")
    parser.add_argument("--platform", help="Primary AI platform (codex, claude-code, cursor, trae, windsurf, gemini)")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, no file writes")
    parser.add_argument("--force", action="store_true", help="Overwrite existing generated files")
    parser.add_argument(
        "--starter",
        dest="starter",
        action="store_true",
        default=None,
        help="Force basic feature starter generation (default: blueprint-driven)",
    )
    parser.add_argument(
        "--no-starter",
        dest="starter",
        action="store_false",
        help="Disable basic feature starter generation",
    )
    args = parser.parse_args()

    generate(args)


if __name__ == "__main__":
    main()
