#!/usr/bin/env python3
"""
AI Bootstrap — Adaptive Wizard v1.0

交互式自适应向导。先检测环境，再根据检测结果动态调整问题数量。
支持 Quick / Normal / Advanced 三种模式。

用法:
    python3 wizard.py --dir /path/to/project
    python3 wizard.py --dir /path/to/project --mode advanced
    python3 wizard.py --dir /path/to/project --mode quick --blueprint go-microservice
    python3 wizard.py --dir /path/to/project --dry-run
"""

import argparse
import json
import os
import subprocess
import sys
import re as regex_module
import shutil as shutil_module
from datetime import datetime
from pathlib import Path
from typing import Optional

from yaml_utils import load_yaml


# ─── Constants ────────────────────────────────────────────────────────────────

SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
BLUEPRINTS_DIR = SKILL_DIR / "templates" / "blueprints"
BOOTSTRAP_VERSION = "1.1.0"


# ─── ANSI Color Helpers ───────────────────────────────────────────────────────

class Style:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"


def _color(code, text):
    """Apply ANSI color if supported."""
    if os.environ.get("CODEX") or (hasattr(sys.stdout, "isatty") and sys.stdout.isatty()):
        return code + text + Style.RESET
    return text


def C(code, text):
    """Short alias for _color."""
    return _color(code, text)


def header(text):
    width = shutil_module.get_terminal_size((60, 20)).columns
    print()
    print(C(Style.CYAN, "\u2501" * width))
    print(C(Style.BOLD + Style.CYAN, "  " + text))
    print(C(Style.CYAN, "\u2501" * width))


def section(text):
    print()
    print(C(Style.BOLD + Style.BLUE, "  \u25c6 " + text))


def ask(prompt_text, default=None, options=None):
    """Display a prompt and get user input."""
    if options:
        opt_str = " / ".join(
            [C(Style.GREEN, o) if i == 0 else o for i, o in enumerate(options)]
        )
        hint = ""
        if default:
            hint = C(Style.GRAY, default)
        else:
            hint = C(Style.GRAY, options[0])
        formatted = "  {} [{}]: ".format(prompt_text, hint)
    elif default:
        formatted = "  {} [{}]: ".format(prompt_text, C(Style.GRAY, default))
    else:
        formatted = "  {}: ".format(prompt_text)

    try:
        user_input = input(formatted).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        print(C(Style.RED, "\n  \u270b \u64cd\u4f5c\u53d6\u6d88"))
        sys.exit(0)

    if not user_input and default:
        return default
    if not user_input and options:
        return options[0]
    return user_input


def confirm(prompt_text, default="Y"):
    """Ask a yes/no question."""
    opts = ["Y", "n"] if default.upper() == "Y" else ["y", "N"]
    result = ask(prompt_text, default=default, options=opts)
    return result.upper() == "Y"


def info(text):
    print("  " + C(Style.GRAY, "\u00b7") + " " + text)


def success(text):
    print("  " + C(Style.GREEN, "\u2713") + " " + C(Style.BOLD, text))


def warning(text):
    print("  " + C(Style.YELLOW, "\u26a0") + " " + text)


def error(text):
    print("  " + C(Style.RED, "\u2717") + " " + text)


def progress(text, done=True):
    icon = C(Style.GREEN, "\u2713") if done else C(Style.YELLOW, "\u22ef")
    print("  " + icon + " " + text)


# ─── Blueprint Registry ──────────────────────────────────────────────────────

def list_blueprints():
    """List all available blueprints with metadata."""
    blueprints = []
    for bp_file in sorted(BLUEPRINTS_DIR.glob("*.yaml")):
        parsed = load_yaml(bp_file)
        bp = {
            "id": parsed.get("id", bp_file.stem),
            "file": str(bp_file),
            "name": parsed.get("name", bp_file.stem),
            "description": parsed.get("description", ""),
            "tags": parsed.get("tags", []),
            "architecture": parsed.get("architecture", {}).get("style", ""),
            "pattern": parsed.get("architecture", {}).get("pattern", ""),
        }
        blueprints.append(bp)

    return blueprints


def _find_bp(blueprints, bp_id):
    """Find a blueprint by ID."""
    for bp in blueprints:
        if bp["id"] == bp_id:
            return bp
    return None


def recommend_blueprint(detection, preferences=None):
    """
    Recommend the best blueprint based on detection results.
    Returns (blueprint_dict, confidence_score).
    """
    blueprints = list_blueprints()
    runtimes = detection.get("environment", {}).get("runtimes", [])
    runtime_names = [r["name"] for r in runtimes]
    project = detection.get("project", {})
    languages = project.get("languages", [])

    detections = []

    # Check framework-specific detections (highest confidence)
    for lang in languages:
        frameworks = lang.get("frameworks", {})
        lang_name = lang.get("name", "").lower()

        if lang_name in {"typescript", "javascript"}:
            if "next" in frameworks:
                detections.append((_find_bp(blueprints, "next-fullstack"), 0.95))
            if "uni-app" in frameworks or "uniapp" in frameworks:
                detections.append((_find_bp(blueprints, "uni-app-nitro"), 0.92))
            if "react" in frameworks:
                detections.append((_find_bp(blueprints, "react-fastapi"), 0.90))
            if "vue" in frameworks or "nuxt" in frameworks:
                detections.append((_find_bp(blueprints, "vue-django"), 0.85))
            if "nestjs" in frameworks:
                detections.append((_find_bp(blueprints, "next-fullstack"), 0.85))

        elif lang_name == "python":
            if "fastapi" in frameworks:
                detections.append((_find_bp(blueprints, "react-fastapi"), 0.80))
                detections.append((_find_bp(blueprints, "python-ml-service"), 0.75))
            if "django" in frameworks:
                detections.append((_find_bp(blueprints, "vue-django"), 0.80))

        elif lang_name == "java":
            if "spring" in frameworks:
                detections.append((_find_bp(blueprints, "react-springboot"), 0.92))
            else:
                detections.append((_find_bp(blueprints, "react-springboot"), 0.70))

        elif lang_name == "go":
            detections.append((_find_bp(blueprints, "go-microservice"), 0.90))

        elif lang_name == "rust":
            detections.append((_find_bp(blueprints, "rust-axum-api"), 0.90))

    # For a new project, use the user's product priorities to rank the
    # representative presets before falling back to the generic default.
    preferences = preferences or {}
    if not detections and detection.get("is_empty", True):
        priority = preferences.get("priority")
        unified_language = preferences.get("unified_language")
        deployment = preferences.get("deployment")
        preferred_id = None
        if priority == "ai" or (priority == "demo" and unified_language == "yes"):
            preferred_id = "nuxt-ai-fullstack"
        elif priority == "enterprise":
            preferred_id = "react-springboot"
        elif priority == "ml":
            preferred_id = "python-ml-service"

        if preferred_id:
            preferred = _find_bp(blueprints, preferred_id)
            if preferred:
                confidence = 0.92 if deployment in {None, "vercel", "local"} else 0.84
                return preferred, confidence

    # Runtime-based recommendations (medium confidence)
    if not detections:
        if "node" in runtime_names:
            detections.append((_find_bp(blueprints, "next-fullstack"), 0.80))
            detections.append((_find_bp(blueprints, "react-fastapi"), 0.75))
        if "python" in runtime_names:
            detections.append((_find_bp(blueprints, "python-ml-service"), 0.65))
            detections.append((_find_bp(blueprints, "react-fastapi"), 0.60))
        if "go" in runtime_names:
            detections.append((_find_bp(blueprints, "go-microservice"), 0.85))
        if "rust" in runtime_names:
            detections.append((_find_bp(blueprints, "rust-axum-api"), 0.85))

    # No detections at all — return default
    if not detections:
        if detection.get("is_empty", True):
            default = _find_bp(blueprints, "next-fullstack")
        else:
            default = blueprints[0] if blueprints else None
        return (default, 0.50) if default else (None, 0.30)

    # Deduplicate: keep highest confidence per blueprint
    seen = set()
    unique = []
    for bp, conf in detections:
        if bp and bp["id"] not in seen:
            seen.add(bp["id"])
            unique.append((bp, conf))

    if not unique:
        return (blueprints[0] if blueprints else None, 0.30)

    unique.sort(key=lambda x: -x[1])
    return unique[0]


# ─── Detection Integration ────────────────────────────────────────────────────

def run_detection(project_dir):
    """Run the detection engine and return structured results."""
    detect_script = SCRIPTS_DIR / "detect.py"
    try:
        result = subprocess.run(
            [sys.executable, str(detect_script), "--dir", project_dir, "--json"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode in (0, 1):
            return json.loads(result.stdout)
        else:
            warning("Detection engine error: " + result.stderr.strip())
            return _empty_detection(project_dir)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
        warning("Detection engine unavailable: " + str(e))
        return _empty_detection(project_dir)


def _empty_detection(project_dir):
    """Return an empty detection result."""
    return {
        "project_dir": project_dir,
        "is_empty": True,
        "environment": {"runtimes": [], "tools": []},
        "project": {"type": "empty", "languages": [], "package_managers": []},
        "repository": {"git": False, "ci_cd": [], "docker": {}},
        "config": {},
        "key_files": [],
    }


# ─── Generation Integration ───────────────────────────────────────────────────

def run_generation(project_dir, blueprint_id, name, description, agents, platform, dry_run=False):
    """Run the generator with collected parameters."""
    generate_script = SCRIPTS_DIR / "generate.py"
    cmd = [
        sys.executable, str(generate_script),
        "--dir", project_dir,
        "--blueprint", blueprint_id,
        "--name", name,
        "--description", description,
        "--agents", agents,
        "--platform", platform,
    ]
    if dry_run:
        cmd.append("--dry-run")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return True, result.stdout
        else:
            error("Generator failed: " + (result.stderr.strip() or "unknown error"))
            return False, result.stdout + "\n" + result.stderr
    except subprocess.TimeoutExpired:
        error("Generator timed out")
        return False, ""


# ─── Parse Blueprint YAML (simple) ───────────────────────────────────────────

def parse_bp_yaml(blueprint_id):
    """Parse blueprint YAML to extract stack details."""
    bp_file = BLUEPRINTS_DIR / (blueprint_id + ".yaml")
    if not bp_file.exists():
        return {
            "id": blueprint_id,
            "name": blueprint_id,
            "stack": {"frontend": {}, "backend": {}, "database": {}},
            "architecture": {},
        }
    return load_yaml(bp_file)


def stack_summary(bp_details):
    """Return a compact, human-readable stack summary for choice cards."""
    stack = bp_details.get("stack", {})
    frontend = stack.get("frontend", {})
    backend = stack.get("backend", {})
    database = stack.get("database", {})
    ai = stack.get("ai", {})
    deployment = stack.get("deployment", {})

    frontend_name = frontend.get("framework", "none")
    if frontend.get("version"):
        frontend_name += " " + str(frontend["version"])
    if frontend.get("ui_library"):
        frontend_name += " + " + str(frontend["ui_library"])

    backend_name = backend.get("framework", "none")
    if backend.get("version"):
        backend_name += " " + str(backend["version"])
    if backend.get("language"):
        backend_name += " / " + str(backend["language"])
    if backend.get("api_style"):
        backend_name += " / " + str(backend["api_style"])

    database_name = database.get("primary", "none")
    if isinstance(database_name, dict):
        database_name = database_name.get("type", "none")
    if database.get("production"):
        database_name += " → " + str(database["production"])

    ai_name = ai.get("sdk", "none")
    deployment_name = deployment.get("platform", deployment.get("type", "none"))
    package_manager = stack.get("package_manager", "none")
    if isinstance(package_manager, dict):
        package_manager = package_manager.get("name", "none")
    apps = bp_details.get("apps", [])
    apps_summary = ""
    if isinstance(apps, list) and apps:
        ids = []
        for app in apps:
            if isinstance(app, dict):
                ids.append(str(app.get("id") or app.get("name") or "?"))
            else:
                ids.append(str(app))
        apps_summary = "单仓多应用({}) | ".format("、".join(ids[:4]))

    return apps_summary + "前端: {} | 后端: {} | AI: {} | 数据库: {} | 部署: {} | 包管理器: {}".format(
        frontend_name, backend_name, ai_name, database_name, deployment_name, package_manager
    )


def write_stack_decision(project_dir, blueprint_id, source="wizard", preferences=None):
    """Persist the user's selected stack after generation succeeds."""
    bp = parse_bp_yaml(blueprint_id)
    out_dir = Path(project_dir) / "docs" / "00-research"
    out_dir.mkdir(parents=True, exist_ok=True)
    decision_path = out_dir / "stack-decision.md"
    if decision_path.exists():
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        decision_path = out_dir / ("stack-decision-{}.md".format(stamp))
        suffix = 2
        while decision_path.exists():
            decision_path = out_dir / ("stack-decision-{}-{}.md".format(stamp, suffix))
            suffix += 1

    stack = bp.get("stack", {})
    content = "# 技术栈决策\n\n"
    content += "> 由 AI Bootstrap Wizard 生成。该文件记录用户确认过的技术方案，后续架构变更需补充 ADR。\n\n"
    content += "- **选择来源**: {}\n".format(source)
    content += "- **Blueprint**: {} v{}\n".format(bp.get("name", blueprint_id), bp.get("version", ""))
    content += "- **方案摘要**: {}\n\n".format(stack_summary(bp))
    if preferences:
        content += "- **选型偏好**: {}\n\n".format(json.dumps(preferences, ensure_ascii=False))
    content += "## 完整组合\n\n"
    content += "```yaml\n{}\n```\n\n".format(json.dumps(stack, ensure_ascii=False, indent=2))
    content += "## 选择理由与代价\n\n"
    content += "- 选择理由：在项目目标、团队能力、交付速度和部署环境之间取得平衡。\n"
    content += "- 主要代价：后续需要关注数据库扩展、AI 长任务异步化和第三方 Provider 迁移。\n"
    content += "\n## 未来迁移触发条件\n\n"
    content += "- 并发写入、复杂报表或长耗时 AI 任务成为主要瓶颈时，迁移到独立数据库、队列或异步任务系统。\n"
    content += "- 团队协作边界、合规要求或部署规模显著变化时，重新评估 Blueprint 并补充 ADR。\n"
    decision_path.write_text(content, encoding="utf-8")
    return decision_path


# ─── Wizard Questions ────────────────────────────────────────────────────────

def ask_project_info():
    """Ask for basic project information."""
    section("\u9879\u76ee\u4fe1\u606f")

    name = ask("\u9879\u76ee\u540d\u79f0", default="my-app")
    name = regex_module.sub(r'[^a-zA-Z0-9-]', '-', name).strip('-').lower() or "my-app"

    # \u7559\u7a7a\u65f6\u7531 generate.py \u81ea\u52a8\u91c7\u7528\u6240\u9009 Blueprint \u7684 description\uff0c\u907f\u514d\u7a7a\u6d1e\u5360\u4f4d\u7b80\u4ecb\u3002
    description = ask("\u9879\u76ee\u63cf\u8ff0\uff08\u53ef\u7559\u7a7a\uff1a\u81ea\u52a8\u91c7\u7528\u6240\u9009 Blueprint \u7684\u63cf\u8ff0\uff09", default="")
    return name, description


def ask_strategy_preferences(mode):
    """Collect the five decisions that materially affect stack selection."""
    section("技术方案偏好")
    info("先回答五个产品级问题，向导会据此推荐典型技术方案。")
    print("    ai         AI 原生应用、AI 交互与生成能力优先")
    print("    demo       快速做出可交互 Demo / MVP")
    print("    enterprise 企业级扩展、团队协作和长期维护")
    print("    ml         模型、数据处理和算法能力优先")
    priority = ask("第一版更看重什么", default="ai", options=["ai", "demo", "enterprise", "ml"])

    print()
    print("    yes        前后端统一使用 TypeScript")
    print("    no         接受 Python / Go 等后端语言")
    unified_language = ask("是否希望前后端统一语言", default="yes", options=["yes", "no"])

    print()
    print("    local      本地 Demo / 单机部署")
    print("    vercel     Vercel / Serverless")
    print("    docker     Docker / 云服务器")
    deployment = ask("预计如何部署", default="vercel", options=["local", "vercel", "docker"])

    print()
    print("    yes        需要独立管理后台 / PC Web")
    print("    no         暂不需要")
    needs_admin = ask("是否需要独立管理后台", default="no", options=["yes", "no"])
    return {
        "priority": priority,
        "unified_language": unified_language,
        "deployment": deployment,
        "needs_admin": needs_admin,
    }


def ask_blueprint(detection, mode, preferences=None):
    """Ask user to select a blueprint, with recommendation."""
    blueprints = list_blueprints()

    recommended, confidence = recommend_blueprint(detection, preferences)
    recommended_id = recommended["id"] if recommended else blueprints[0]["id"]

    section("\u9009\u62e9 Blueprint")

    if mode == "quick" and recommended:
        runtimes = detection.get("environment", {}).get("runtimes", [])
        rt_names = [r["name"] for r in runtimes]
        if rt_names:
            info("\u68c0\u6d4b\u5230\u73af\u5883: " + ", ".join(rt_names))
        success("\u63a8\u8350: " + C(Style.BOLD, recommended["name"]) +
                " (" + recommended.get("description", "") + ")")
        info("技术方案: " + stack_summary(parse_bp_yaml(recommended["id"])))
        info("\u7f6e\u4fe1\u5ea6: {:.0%}".format(confidence))
        alternatives = [bp for bp in blueprints if bp["id"] != recommended["id"]][:2]
        if alternatives:
            info("可替代方案: " + "、".join(bp["name"] for bp in alternatives))
        print()
        text = "\u4f7f\u7528\u63a8\u8350 Blueprint\u300c{}\u300d".format(recommended["name"])
        if confirm(text, default="Y"):
            return recommended["id"]

    # Show all blueprints
    print()
    info("\u53ef\u7528典型技术方案（先看组合，再选择 Blueprint）:")
    for i, bp in enumerate(blueprints, 1):
        marker = " " + C(Style.GREEN, "\u2605 \u63a8\u8350") if bp["id"] == recommended_id else ""
        tags = C(Style.GRAY, " [" + ", ".join(bp.get("tags", [])) + "]")
        desc = C(Style.GRAY, bp.get("description", ""))
        details = parse_bp_yaml(bp["id"])
        print("    {}. {}{}".format(
            C(Style.CYAN, str(i)),
            C(Style.BOLD, bp["name"]) + tags + marker,
        ))
        print("       " + desc)
        print("       " + C(Style.GRAY, stack_summary(details)))

    print()
    default_idx = 1
    for i, bp in enumerate(blueprints, 1):
        if bp["id"] == recommended_id:
            default_idx = i
            break

    choice = ask("\u9009\u62e9 Blueprint (1-{})".format(len(blueprints)),
                 default=str(default_idx))

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(blueprints):
            return blueprints[idx]["id"]
    except ValueError:
        pass

    for bp in blueprints:
        if choice.lower() in bp["id"].lower() or choice.lower() in bp["name"].lower():
            return bp["id"]

    warning("\u65e0\u6548\u8f93\u5165\uff0c\u4f7f\u7528\u9ed8\u8ba4: " + recommended_id)
    return recommended_id


def ask_agents(mode):
    """Ask about AI agents configuration."""
    section("AI Agent \u914d\u7f6e")

    all_agents = [
        ("codex", "Codex", "\u5168\u6808\u5f00\u53d1\u3001\u67b6\u6784\u8bbe\u8ba1"),
        ("claude-code", "Claude Code", "\u540e\u7aef\u5f00\u53d1\u3001\u6d4b\u8bd5"),
        ("cursor", "Cursor", "\u524d\u7aef\u5f00\u53d1\u3001\u5b9e\u65f6\u7f16\u7801"),
        ("trae", "Trae", "\u96f6\u57fa\u7840\u5feb\u901f\u5f00\u53d1"),
        ("windsurf", "Windsurf", "\u4ee3\u7801\u5bfc\u822a"),
        ("gemini", "Gemini CLI", "\u6570\u636e\u5904\u7406\u3001AI/ML"),
    ]

    if mode == "quick":
        agents = ask("\u53c2\u4e0e\u7684 AI Agent (\u9017\u53f7\u5206\u9694)",
                     default="codex, cursor")
        platform = ask("\u4e3b\u8981 AI \u5e73\u53f0", default="codex",
                       options=[a[0] for a in all_agents])
        return agents, platform

    info("\u53ef\u7528 AI Agent:")
    for i, (aid, aname, adesc) in enumerate(all_agents, 1):
        print("    {}. {:20s} {}".format(
            C(Style.CYAN, str(i)),
            C(Style.BOLD, aname),
            C(Style.GRAY, adesc),
        ))

    print()
    agents_input = ask("\u53c2\u4e0e\u7684 Agent (\u7f16\u53f7/\u540d\u79f0, \u9017\u53f7\u5206\u9694)",
                       default="1, 3")
    selected = []
    for part in agents_input.split(","):
        part = part.strip()
        if part.isdigit():
            idx = int(part) - 1
            if 0 <= idx < len(all_agents):
                selected.append(all_agents[idx][0])
        else:
            for aid, aname, _ in all_agents:
                if part.lower() in aid.lower() or part.lower() in aname.lower():
                    selected.append(aid)
                    break

    agents = ", ".join(selected if selected else ["codex", "cursor"])
    platform = ask("\u4e3b\u8981 AI \u5e73\u53f0",
                   default=selected[0] if selected else "codex",
                   options=[a[0] for a in all_agents])
    return agents, platform


def ask_deployment(mode):
    """Ask about deployment configuration."""
    section("\u90e8\u7f72\u914d\u7f6e")

    need_docker = False
    need_ci = False

    if confirm("\u9700\u8981 Docker \u5bb9\u5668\u5316\u652f\u6301", default="Y"):
        need_docker = True
    if mode != "quick":
        if confirm("\u9700\u8981 CI/CD \u6d41\u6c34\u7ebf", default="Y"):
            need_ci = True
    return need_docker, need_ci


# ─── Summary Display ─────────────────────────────────────────────────────────

def show_summary(name, description, blueprint, agents_list, platform,
                 project_dir, mode, need_docker=False, need_ci=False, bp_details=None):
    """Show a summary of all choices before generation."""
    header("\u786e\u8ba4\u914d\u7f6e")

    info("\u6a21\u5f0f:      " + C(Style.BOLD, mode.upper()))
    info("\u9879\u76ee\u76ee\u5f55:    " + project_dir)
    print()
    info("\u9879\u76ee\u540d\u79f0:    " + C(Style.BOLD, name))
    info("\u9879\u76ee\u63cf\u8ff0:    " + description)
    print()
    info("Blueprint:   " + C(Style.BOLD, blueprint.get("name", blueprint["id"])))

    if bp_details:
        stack = bp_details.get("stack", {})
        frontend = stack.get("frontend", {})
        database = stack.get("database", {})
        ai = stack.get("ai", {})
        deployment = stack.get("deployment", {})
        primary_db = database.get("primary", "N/A")
        if isinstance(primary_db, dict):
            primary_db = primary_db.get("type", "N/A")
        info("完整技术栈: " + stack_summary(bp_details))
        info("UI 库:       " + str(frontend.get("ui_library", "none")))
        info("AI SDK:      " + str(ai.get("sdk", "none")))
        info("生产数据库:   " + str(database.get("production", primary_db)))
        info("部署平台:     " + str(deployment.get("platform", "none")))
        info("架构:         " + str(bp_details.get("architecture", {}).get("style", "N/A")))

    info("\u9644\u52a0 Docker: " + ("Yes" if need_docker else "No"))
    info("CI/CD:       " + ("Yes" if need_ci else "No"))
    print()
    info("AI Agent:    " + ", ".join(agents_list))
    info("\u4e3b\u5e73\u53f0:      " + platform)
    print()


# ─── Main Wizard Flow ────────────────────────────────────────────────────────

def run_wizard(args):
    """Run the interactive wizard."""
    project_dir = Path(args.dir).resolve()
    project_dir.mkdir(parents=True, exist_ok=True)

    mode = args.mode.lower()
    force_blueprint = args.blueprint
    dry_run = args.dry_run
    selection_source = "wizard"
    preferences = {}

    header("AI Bootstrap Wizard v{}".format(BOOTSTRAP_VERSION))

    mode_desc = {
        "quick": "\u5feb\u901f\u6a21\u5f0f \u2014 \u53ea\u8be2\u95ee\u5173\u952e\u95ee\u9898\uff0c\u4f7f\u7528\u63a8\u8350\u9ed8\u8ba4\u503c",
        "normal": "\u6807\u51c6\u6a21\u5f0f \u2014 \u5b8c\u6574\u5f15\u5bfc\uff0c\u6bcf\u4e2a\u6b65\u9aa4\u90fd\u6709\u9009\u62e9\u7a7a\u95f4",
        "advanced": "\u9ad8\u7ea7\u6a21\u5f0f \u2014 \u81ea\u5b9a\u4e49\u6bcf\u4e2a\u6280\u672f\u9009\u578b\u7ec6\u8282",
    }
    info(C(Style.BOLD, "\u6a21\u5f0f: " + mode.upper()))
    info(C(Style.GRAY, mode_desc.get(mode, "")))
    print()

    # ─── Step 1: Detection ───
    progress("\u68c0\u6d4b\u9879\u76ee\u73af\u5883...", done=False)
    detection = run_detection(str(project_dir))
    is_empty = detection.get("is_empty", True)

    if is_empty:
        progress("\u7a7a\u76ee\u5f55 \u2014 \u5168\u65b0\u9879\u76ee")
    else:
        ptype = detection.get("project", {}).get("type", "unknown")
        langs = detection.get("project", {}).get("languages", [])
        parts = []
        for l in langs:
            fws = l.get("frameworks", {})
            if fws:
                parts.append("{} ({})".format(l["name"], list(fws.keys())[0]))
            else:
                parts.append(l["name"])
        progress("\u68c0\u6d4b\u5230\u9879\u76ee: " + C(Style.BOLD, ptype) +
                 " [" + ", ".join(parts) + "]")

    # Show runtimes
    runtimes = detection.get("environment", {}).get("runtimes", [])
    if runtimes:
        parts = []
        for r in runtimes:
            ver = r.get("version", "")
            parts.append(r["name"] + " " + ver)
        info("\u8fd0\u884c\u65f6: " + ", ".join(parts))

    git = detection.get("repository", {}).get("git", False)
    if git:
        info("Git: " + detection["repository"].get("branch", "detected"))
    print()

    # ─── Step 2: Project Info ───
    name, description = ask_project_info()
    print()

    # ─── Step 3: Blueprint ───
    if force_blueprint and force_blueprint != "auto":
        all_bps = list_blueprints()
        found = _find_bp(all_bps, force_blueprint)
        if found:
            blueprint_id = force_blueprint
            selection_source = "explicit --blueprint"
            info("\u4f7f\u7528\u6307\u5b9a Blueprint: " + C(Style.BOLD, found["name"]))
        else:
            warning("Blueprint '{}' \u4e0d\u5b58\u5728\uff0c\u4f7f\u7528\u63a8\u8350".format(force_blueprint))
            preferences = ask_strategy_preferences(mode)
            blueprint_id = ask_blueprint(detection, mode, preferences)
    else:
        preferences = ask_strategy_preferences(mode)
        blueprint_id = ask_blueprint(detection, mode, preferences)

    all_bps = list_blueprints()
    selected_bp = next((bp for bp in all_bps if bp["id"] == blueprint_id), all_bps[0])
    bp_details = parse_bp_yaml(blueprint_id)
    if not (description or "").strip():
        description = str(selected_bp.get("description") or "").strip()
        if description:
            info("\u9879\u76ee\u63cf\u8ff0\u7559\u7a7a\uff0c\u81ea\u52a8\u91c7\u7528 Blueprint \u63cf\u8ff0\u3002")
    print()

    # ─── Step 4: Deployment ───
    need_docker, need_ci = ask_deployment(mode)
    print()

    # ─── Step 5: Agents ───
    agents_str, platform = ask_agents(mode)
    agents_list = [a.strip() for a in agents_str.split(",") if a.strip()]
    print()

    # ─── Step 6: Summary ───
    show_summary(
        name=name,
        description=description,
        blueprint=selected_bp,
        agents_list=agents_list,
        platform=platform,
        project_dir=str(project_dir),
        mode=mode,
        need_docker=need_docker,
        need_ci=need_ci,
        bp_details=bp_details,
    )

    if not confirm("\u4f7f\u7528\u4ee5\u4e0a\u914d\u7f6e\u751f\u6210\u9879\u76ee", default="Y"):
        print()
        info(C(Style.YELLOW, "\u64cd\u4f5c\u5df2\u53d6\u6d88"))
        sys.exit(0)

    print()

    # ─── Step 7: Generate ───
    header("\u751f\u6210\u6587\u4ef6")

    gen_ok, gen_output = run_generation(
        project_dir=str(project_dir),
        blueprint_id=blueprint_id,
        name=name,
        description=description,
        agents=agents_str,
        platform=platform,
        dry_run=dry_run,
    )

    if dry_run:
        print(gen_output)
        print()
        info(C(Style.YELLOW, "Dry-run \u5b8c\u6210\u3002\u79fb\u9664 --dry-run \u5411\u6267\u884c\u5b9e\u9645\u751f\u6210\u3002"))
        return True

    if gen_ok:
        decision_path = write_stack_decision(
            project_dir,
            blueprint_id,
            source=selection_source,
            preferences=preferences,
        )
        print()
        header(C(Style.GREEN, "\u2713  Bootstrap \u5b8c\u6210"))
        info("\u9879\u76ee:      " + C(Style.BOLD, name))
        info("Blueprint: " + C(Style.BOLD, selected_bp["name"]))
        info("\u76ee\u5f55:      " + str(project_dir))
        info("Agent:     " + ", ".join(agents_list))
        info("\u6280\u672f\u6808\u51b3\u7b56: " + str(decision_path))

        print()
        val_cmd = "python3 {} --dir {}".format(SCRIPTS_DIR / "validate.py", project_dir)
        info(C(Style.GRAY, "\u9a8c\u8bc1\u68c0\u67e5: "))
        print("  " + C(Style.CYAN, val_cmd))
        print()

        # ─── Step 8: Optional validation ───
        if confirm("\u7acb\u5373\u8fd0\u884c\u9a8c\u8bc1\u68c0\u67e5", default="Y"):
            print()
            subprocess.run([sys.executable, str(SCRIPTS_DIR / "validate.py"),
                           "--dir", str(project_dir)])
    else:
        error("\u751f\u6210\u5931\u8d25\uff0c\u8bf7\u68c0\u67e5\u9519\u8bef\u4fe1\u606f")
        sys.exit(1)

    return True


# ─── CLI Entry ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AI Bootstrap \u2014 Adaptive Wizard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
\u6a21\u5f0f\u8bf4\u660e:
  quick     \u5feb\u901f\u6a21\u5f0f (\u9ed8\u8ba4) \u2014 \u63a8\u8350 Blueprint + \u5c11\u91cf\u5173\u952e\u95ee\u9898
  normal    \u6807\u51c6\u6a21\u5f0f \u2014 \u5b8c\u6574\u5f15\u5bfc\uff0c\u66f4\u591a\u9009\u62e9\u7a7a\u95f4
  advanced  \u9ad8\u7ea7\u6a21\u5f0f \u2014 \u81ea\u5b9a\u4e49\u6bcf\u4e2a\u6280\u672f\u9009\u578b

\u793a\u4f8b:
  python3 wizard.py --dir ./my-project
  python3 wizard.py --dir ./my-project --mode advanced
  python3 wizard.py --dir ./my-project --mode quick --blueprint go-microservice
  python3 wizard.py --dir ./my-project --dry-run
        """,
    )
    parser.add_argument("--dir", required=True, help="\u76ee\u6807\u9879\u76ee\u76ee\u5f55")
    parser.add_argument("--mode", default="quick", choices=["quick", "normal", "advanced"],
                        help="Wizard \u6a21\u5f0f (\u9ed8\u8ba4: quick)")
    parser.add_argument("--blueprint", default=None,
                        help="\u6307\u5b9a Blueprint ID (\u8df3\u8fc7\u9009\u62e9\u6b65\u9aa4)")
    parser.add_argument("--dry-run", action="store_true",
                        help="\u9884\u89c8\u6a21\u5f0f\uff0c\u4e0d\u5199\u5165\u6587\u4ef6")
    args = parser.parse_args()

    run_wizard(args)


if __name__ == "__main__":
    main()
