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
from pathlib import Path
from typing import Optional

from yaml_utils import load_yaml


# ─── Constants ────────────────────────────────────────────────────────────────

SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
BLUEPRINTS_DIR = SKILL_DIR / "templates" / "blueprints"
BOOTSTRAP_VERSION = "1.0.0"


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


def recommend_blueprint(detection):
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

        elif lang_name == "go":
            detections.append((_find_bp(blueprints, "go-microservice"), 0.90))

        elif lang_name == "rust":
            detections.append((_find_bp(blueprints, "rust-axum-api"), 0.90))

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


# ─── Wizard Questions ────────────────────────────────────────────────────────

def ask_project_info():
    """Ask for basic project information."""
    section("\u9879\u76ee\u4fe1\u606f")

    name = ask("\u9879\u76ee\u540d\u79f0", default="my-app")
    name = regex_module.sub(r'[^a-zA-Z0-9-]', '-', name).strip('-').lower() or "my-app"

    description = ask("\u9879\u76ee\u63cf\u8ff0", default="AI Native Project")
    return name, description


def ask_blueprint(detection, mode):
    """Ask user to select a blueprint, with recommendation."""
    blueprints = list_blueprints()

    recommended, confidence = recommend_blueprint(detection)
    recommended_id = recommended["id"] if recommended else blueprints[0]["id"]

    section("\u9009\u62e9 Blueprint")

    if mode == "quick" and recommended:
        runtimes = detection.get("environment", {}).get("runtimes", [])
        rt_names = [r["name"] for r in runtimes]
        if rt_names:
            info("\u68c0\u6d4b\u5230\u73af\u5883: " + ", ".join(rt_names))
        success("\u63a8\u8350: " + C(Style.BOLD, recommended["name"]) +
                " (" + recommended.get("description", "") + ")")
        info("\u7f6e\u4fe1\u5ea6: {:.0%}".format(confidence))
        print()
        text = "\u4f7f\u7528\u63a8\u8350 Blueprint\u300c{}\u300d".format(recommended["name"])
        if confirm(text, default="Y"):
            return recommended["id"]

    # Show all blueprints
    print()
    info("\u53ef\u7528 Blueprint:")
    for i, bp in enumerate(blueprints, 1):
        marker = " " + C(Style.GREEN, "\u2605 \u63a8\u8350") if bp["id"] == recommended_id else ""
        tags = C(Style.GRAY, " [" + ", ".join(bp.get("tags", [])) + "]")
        desc = C(Style.GRAY, bp.get("description", ""))
        print("    {}. {}{}".format(
            C(Style.CYAN, str(i)),
            C(Style.BOLD, bp["name"]) + tags + marker,
        ))
        print("       " + desc)

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
                 project_dir, mode, need_docker=False, bp_details=None):
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
        fe = bp_details.get("stack", {}).get("frontend", {}).get("framework", "N/A")
        be = bp_details.get("stack", {}).get("backend", {}).get("framework", "N/A")
        db = bp_details.get("stack", {}).get("database", {}).get("primary", "N/A")
        arch = bp_details.get("architecture", {}).get("style", "N/A")
        info("\u524d\u7aef:       " + fe)
        info("\u540e\u7aef:       " + be)
        info("\u6570\u636e\u5e93:      " + db)
        info("\u67b6\u6784:       " + arch)

    info("\u90e8\u7f72:       " + ("Docker" if need_docker else "None"))
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
            info("\u4f7f\u7528\u6307\u5b9a Blueprint: " + C(Style.BOLD, found["name"]))
        else:
            warning("Blueprint '{}' \u4e0d\u5b58\u5728\uff0c\u4f7f\u7528\u63a8\u8350".format(force_blueprint))
            blueprint_id = ask_blueprint(detection, mode)
    else:
        blueprint_id = ask_blueprint(detection, mode)

    all_bps = list_blueprints()
    selected_bp = next((bp for bp in all_bps if bp["id"] == blueprint_id), all_bps[0])
    bp_details = parse_bp_yaml(blueprint_id)
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
        print()
        header(C(Style.GREEN, "\u2713  Bootstrap \u5b8c\u6210"))
        info("\u9879\u76ee:      " + C(Style.BOLD, name))
        info("Blueprint: " + C(Style.BOLD, selected_bp["name"]))
        info("\u76ee\u5f55:      " + str(project_dir))
        info("Agent:     " + ", ".join(agents_list))

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
