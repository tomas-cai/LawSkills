#!/usr/bin/env python3
"""
AI Bootstrap — Validation Engine v1.0

Validates Bootstrap output: file integrity, blueprint consistency, token completeness,
agent context correctness, and syntax validation.

Usage:
    python3 validate.py --dir /path/to/project
    python3 validate.py --dir /path/to/project --fix
    python3 validate.py --dir /path/to/project --json
"""

import argparse
import json
import os
import sys
import re
from datetime import datetime
from pathlib import Path

from yaml_utils import load_yaml, load_yaml_text
from framework_gate import DEPRECATED_COMPONENTS

from layout import (
    ADR_DIR,
    ADR_INDEX_PATH,
    CURRENT_TASKS_PATH,
    DECISION_INDEX_PATH,
    DESIGN_PATH,
    DESIGN_TOKEN_SPEC_PATH,
    INITIAL_ADR_PATH,
    MANIFEST_PATH,
    MEMORY_PATH,
    PROJECT_PROFILE_PATH,
    REQUIRED_DIRECTORIES,
    REVIEW_INDEX_PATH,
)

SKILL_DIR = Path(__file__).resolve().parent.parent
BLUEPRINTS_DIR = SKILL_DIR / "templates" / "blueprints"


# ─── Validation Result Models ────────────────────────────────────────────────

class ValidationCheck:
    def __init__(self, name: str, description: str, severity: str = "error"):
        self.name = name
        self.description = description
        self.severity = severity  # error | warning | info
        self.status = "pending"  # passed | failed | warning | skipped
        self.details = {}
        self.errors = []
        self.warnings = []

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "status": self.status,
            "severity": self.severity,
            "details": self.details,
            "errors": self.errors,
            "warnings": self.warnings,
        }


class ValidationReport:
    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        self.timestamp = datetime.now().isoformat()
        self.checks: list[ValidationCheck] = []
        self.summary = {"passed": 0, "warnings": 0, "failures": 0, "score": 0}

    def add_check(self, check: ValidationCheck):
        self.checks.append(check)
        if check.status == "passed":
            self.summary["passed"] += 1
        elif check.status == "warning":
            self.summary["warnings"] += 1
        elif check.status == "skipped":
            self.summary.setdefault("skipped", 0)
            self.summary["skipped"] += 1
        else:
            self.summary["failures"] += 1

    def compute_score(self) -> int:
        total = sum(1 for c in self.checks if c.status != "skipped")
        if total == 0:
            return 0
        passed_score = (self.summary["passed"] / total) * 70
        warning_penalty = (self.summary["warnings"] / total) * 20
        failure_penalty = (self.summary["failures"] / total) * 100
        score = max(0, min(100, passed_score - warning_penalty + 30))
        self.summary["score"] = round(score)
        return self.summary["score"]

    def get_status(self) -> str:
        if self.summary["failures"] > 0:
            return "failed"
        if self.summary["warnings"] > 0:
            return "warning"
        return "passed"

    def to_dict(self) -> dict:
        return {
            "project_dir": self.project_dir,
            "timestamp": self.timestamp,
            "status": self.get_status(),
            "summary": self.summary,
            "checks": [c.to_dict() for c in self.checks],
        }


# ─── Validation Checks ────────────────────────────────────────────────────────

def _read_frontmatter(path: Path) -> dict:
    """Read YAML frontmatter from a Markdown governance file."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    return load_yaml_text(parts[1].strip())


def _has_path(value: dict, path: tuple[str, ...]) -> bool:
    current = value
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return False
        current = current[key]
    return current not in (None, "")

def check_file_integrity(project_path: Path, report: ValidationReport) -> None:
    """Check all required governance files exist."""
    check = ValidationCheck(
        "file-integrity",
        "Check that all required governance files exist",
    )

    required_files = [
        Path("AGENTS.md"),
        PROJECT_PROFILE_PATH,
        DESIGN_PATH,
        DESIGN_TOKEN_SPEC_PATH,
        MEMORY_PATH,
        ADR_INDEX_PATH,
        CURRENT_TASKS_PATH,
        DECISION_INDEX_PATH,
        REVIEW_INDEX_PATH,
        MANIFEST_PATH,
    ]

    missing = []
    empty = []
    present = []

    for f in required_files:
        fpath = project_path / f
        if fpath.exists():
            size = fpath.stat().st_size
            if size == 0:
                empty.append(str(f))
            else:
                present.append(str(f))
        else:
            missing.append(str(f))

    check.details = {
        "required": len(required_files),
        "present": len(present),
        "missing": missing,
        "empty_files": empty,
    }

    if missing:
        check.status = "failed"
        check.errors = [f"Missing required file: {f}" for f in missing]
    elif empty:
        check.status = "warning"
        check.warnings = [f"Empty file: {f}" for f in empty]
    else:
        check.status = "passed"

    report.add_check(check)


def check_blueprint_consistency(project_path: Path, report: ValidationReport) -> None:
    """Check that generated files are consistent with the blueprint declaration."""
    check = ValidationCheck(
        "blueprint-consistency",
        "Verify generated files match the declared blueprint",
    )

    # Read bootstrap manifest
    manifest_path = project_path / MANIFEST_PATH
    blueprint_id = None
    manifest = {}
    if manifest_path.exists():
        try:
            manifest = load_yaml(manifest_path)
            blueprint_id = manifest.get("manifest", {}).get("blueprint", {}).get("id")
        except Exception:
            pass

    # Read AGENTS.md for blueprint reference
    agents_path = project_path / "AGENTS.md"
    agents_has_blueprint = False
    if agents_path.exists():
        try:
            text = agents_path.read_text(encoding="utf-8")
            if "blueprint" in text.lower():
                agents_has_blueprint = True
        except Exception:
            pass

    # Read PROJECT_PROFILE.md for tech stack and cross-check the declared Blueprint.
    profile_path = project_path / PROJECT_PROFILE_PATH
    profile_has_stack = False
    profile_blueprint_id = None
    profile = {}
    if profile_path.exists():
        try:
            profile = _read_frontmatter(profile_path)
            dna = profile.get("dna", {})
            profile_has_stack = isinstance(dna.get("tech_stack"), dict)
            profile_blueprint_id = dna.get("governance", {}).get("blueprint_id")
        except Exception:
            pass

    check.details = {
        "blueprint_id": blueprint_id or "unknown",
        "agents_file_references_blueprint": agents_has_blueprint,
        "profile_contains_stack": profile_has_stack,
        "profile_blueprint_id": profile_blueprint_id or "unknown",
    }

    issues = []
    if not agents_has_blueprint:
        issues.append("AGENTS.md does not reference a blueprint")
    if not profile_has_stack:
        issues.append("docs/PROJECT_PROFILE.md missing tech stack definition")
    if blueprint_id and profile_blueprint_id and blueprint_id != profile_blueprint_id:
        issues.append(f"Blueprint mismatch: manifest={blueprint_id}, profile={profile_blueprint_id}")
    if blueprint_id:
        blueprint_path = BLUEPRINTS_DIR / f"{blueprint_id}.yaml"
        if blueprint_path.exists() and isinstance(profile, dict):
            try:
                blueprint = load_yaml(blueprint_path)
                expected_stack = blueprint.get("stack", {})
                actual_stack = profile.get("dna", {}).get("tech_stack", {})
                expected_values = {
                    "frontend.framework": expected_stack.get("frontend", {}).get("framework"),
                    "backend.framework": expected_stack.get("backend", {}).get("framework"),
                    "database.primary.type": expected_stack.get("database", {}).get("primary"),
                }
                actual_values = {
                    "frontend.framework": actual_stack.get("frontend", {}).get("framework"),
                    "backend.framework": actual_stack.get("backend", {}).get("framework"),
                    "database.primary.type": actual_stack.get("database", {}).get("primary", {}).get("type"),
                }
                for key, expected in expected_values.items():
                    if expected not in (None, "") and actual_values[key] != expected:
                        issues.append(
                            f"Tech stack mismatch: {key}={actual_values[key]!r}, expected {expected!r}"
                        )
            except Exception as exc:
                issues.append(f"Cannot compare Blueprint tech stack: {exc}")

    if issues:
        check.status = "warning"
        check.warnings = issues
    else:
        check.status = "passed"

    report.add_check(check)


def check_dna_completeness(project_path: Path, report: ValidationReport) -> None:
    """Check that PROJECT_PROFILE.md contains all essential DNA fields."""
    check = ValidationCheck(
        "dna-completeness",
        "Verify PROJECT_PROFILE.md contains all essential DNA fields",
    )

    profile_path = project_path / PROJECT_PROFILE_PATH
    if not profile_path.exists():
        check.status = "failed"
        check.errors = ["docs/PROJECT_PROFILE.md not found"]
        report.add_check(check)
        return

    try:
        text = profile_path.read_text(encoding="utf-8")
    except Exception:
        check.status = "failed"
        check.errors = ["Cannot read docs/PROJECT_PROFILE.md"]
        report.add_check(check)
        return

    has_frontmatter = text.startswith("---")
    dna = {}
    parse_error = None
    if has_frontmatter:
        try:
            dna = _read_frontmatter(profile_path).get("dna", {})
        except Exception as exc:
            parse_error = str(exc)

    required_paths = [
        ("id", ("id",)),
        ("name", ("name",)),
        ("description", ("description",)),
        ("tech_stack", ("tech_stack",)),
        ("architecture", ("architecture",)),
        ("governance", ("governance",)),
    ]
    missing_sections = [label for label, path in required_paths if not _has_path(dna, path)]

    check.details = {
        "has_frontmatter": has_frontmatter,
        "missing_sections": missing_sections,
        "parse_error": parse_error,
    }

    issues = []
    if missing_sections:
        issues.append(f"Missing sections: {', '.join(missing_sections)}")
    if parse_error:
        issues.append(f"Invalid YAML frontmatter: {parse_error}")

    if not has_frontmatter:
        check.status = "warning"
        check.warnings = ["No YAML frontmatter detected"] + issues
    elif issues:
        check.status = "warning"
        check.warnings = issues
    else:
        check.status = "passed"

    report.add_check(check)


def check_design_token_spec(project_path: Path, report: ValidationReport) -> None:
    """Verify the generated design contract matches the selected frontend stack."""
    check = ValidationCheck(
        "design-token-spec",
        "Verify stack-aware design token specification exists and names its theme entry",
    )
    spec_path = project_path / DESIGN_TOKEN_SPEC_PATH
    manifest_path = project_path / MANIFEST_PATH
    blueprint_id = None
    if manifest_path.exists():
        try:
            blueprint_id = load_yaml(manifest_path).get("manifest", {}).get("blueprint", {}).get("id")
        except Exception:
            blueprint_id = None

    if not spec_path.exists():
        check.status = "failed"
        check.errors = [f"Missing required design token spec: {DESIGN_TOKEN_SPEC_PATH}"]
        report.add_check(check)
        return

    try:
        text = spec_path.read_text(encoding="utf-8")
    except Exception as exc:
        check.status = "failed"
        check.errors = [f"Cannot read {DESIGN_TOKEN_SPEC_PATH}: {exc}"]
        report.add_check(check)
        return

    expected_ui = None
    frontend = {}
    if blueprint_id:
        blueprint_path = BLUEPRINTS_DIR / f"{blueprint_id}.yaml"
        if blueprint_path.exists():
            try:
                blueprint = load_yaml(blueprint_path)
                frontend = blueprint.get("stack", {}).get("frontend", {})
                expected_ui = frontend.get("ui_library")
            except Exception:
                pass

    required_markers = [
        "## 2. 技术栈主题入口",
        "## 3. 语义颜色",
        "## 4. Typography scale",
        "## 5. Layout、shape 与行为",
        "## 6. 组件基线",
        "## 8. 首屏验收清单",
    ]
    missing_markers = [marker for marker in required_markers if marker not in text]
    issues = []
    if "{{" in text or "{%" in text:
        issues.append("design token spec contains unresolved template markers")
    if frontend.get("framework") not in (None, "", "none"):
        if expected_ui and expected_ui not in text:
            issues.append(f"design token spec does not reference selected UI library: {expected_ui}")
        if missing_markers:
            issues.append("design token spec missing sections: " + ", ".join(missing_markers))
    elif "不包含前端界面" not in text:
        issues.append("backend-only Blueprint must explicitly mark design tokens as not applicable")

    check.details = {
        "path": str(DESIGN_TOKEN_SPEC_PATH),
        "blueprint_id": blueprint_id or "unknown",
        "ui_library": expected_ui or "none",
        "missing_sections": missing_markers,
    }
    if issues:
        check.status = "failed"
        check.errors = issues
    else:
        check.status = "passed"
    report.add_check(check)


def check_project_layout(project_path: Path, report: ValidationReport) -> None:
    """Verify stack-specific directory layout is documented in generated files."""
    check = ValidationCheck(
        "project-layout",
        "Verify stack-specific directory layout is documented",
    )

    design_path = project_path / DESIGN_PATH
    if not design_path.exists():
        check.status = "failed"
        check.errors = ["docs/DESIGN.md not found"]
        report.add_check(check)
        return

    try:
        design_text = design_path.read_text(encoding="utf-8")
    except Exception as exc:
        check.status = "failed"
        check.errors = [f"Cannot read docs/DESIGN.md: {exc}"]
        report.add_check(check)
        return

    readme_path = project_path / "README.md"
    readme_text = None
    if readme_path.exists():
        try:
            readme_text = readme_path.read_text(encoding="utf-8")
        except Exception as exc:
            check.status = "failed"
            check.errors = [f"Cannot read README.md: {exc}"]
            report.add_check(check)
            return

    profile_path = project_path / PROJECT_PROFILE_PATH
    profile_text = None
    if profile_path.exists():
        try:
            profile_text = profile_path.read_text(encoding="utf-8")
        except Exception as exc:
            check.status = "failed"
            check.errors = [f"Cannot read docs/PROJECT_PROFILE.md: {exc}"]
            report.add_check(check)
            return

    issues = []
    if "项目目录契约" not in design_text or "| 目录 | 职责 |" not in design_text:
        issues.append("docs/DESIGN.md missing stack-specific directory contract")
    if readme_text is not None and "AI Bootstrap" in readme_text and "应用源码目录" not in readme_text:
        issues.append("README.md missing stack-specific application layout section")
    if profile_text is not None and "项目目录契约" not in profile_text:
        issues.append("docs/PROJECT_PROFILE.md missing stack-specific directory contract")

    blueprint_id = None
    manifest_path = project_path / MANIFEST_PATH
    if manifest_path.exists():
        try:
            blueprint_id = load_yaml(manifest_path).get("manifest", {}).get("blueprint", {}).get("id")
        except Exception:
            blueprint_id = None

    if blueprint_id:
        blueprint_path = BLUEPRINTS_DIR / f"{blueprint_id}.yaml"
        if blueprint_path.exists():
            try:
                blueprint = load_yaml(blueprint_path)
                key_dirs = blueprint.get("layout", {}).get("key_dirs", {})
                if isinstance(key_dirs, dict) and key_dirs:
                    declared_path = next(iter(key_dirs))
                    if declared_path not in design_text:
                        issues.append(f"docs/DESIGN.md does not document declared layout path: {declared_path}")
            except Exception:
                pass

    check.details = {
        "blueprint_id": blueprint_id or "unknown",
        "readme_checked": readme_text is not None,
        "profile_checked": profile_text is not None,
        "design_has_contract": "项目目录契约" in design_text,
    }
    if issues:
        check.status = "warning"
        check.warnings = issues
    else:
        check.status = "passed"
    report.add_check(check)


def check_recommended_skills(project_path: Path, report: ValidationReport) -> None:
    """Verify Blueprint-declared AI skills are surfaced in generated docs."""
    check = ValidationCheck(
        "recommended-skills",
        "Verify recommended AI skills are documented for agents and humans",
    )

    manifest_path = project_path / MANIFEST_PATH
    blueprint_id = None
    skills = []
    if manifest_path.exists():
        try:
            blueprint_id = load_yaml(manifest_path).get("manifest", {}).get("blueprint", {}).get("id")
        except Exception:
            blueprint_id = None

    if blueprint_id:
        blueprint_path = BLUEPRINTS_DIR / f"{blueprint_id}.yaml"
        if blueprint_path.exists():
            try:
                skills = load_yaml(blueprint_path).get("skills", [])
            except Exception:
                skills = []

    check.details = {
        "blueprint_id": blueprint_id or "unknown",
        "declared_skills": len(skills) if isinstance(skills, list) else 0,
    }
    if not isinstance(skills, list) or not skills:
        check.status = "passed"
        report.add_check(check)
        return

    install_cmd = ""
    if isinstance(skills[0], dict):
        install_cmd = skills[0].get("install", "")

    targets = [
        ("AGENTS.md", project_path / "AGENTS.md"),
        ("docs/PROJECT_PROFILE.md", project_path / PROJECT_PROFILE_PATH),
    ]
    readme_path = project_path / "README.md"
    if readme_path.exists():
        try:
            if "AI Bootstrap" in readme_path.read_text(encoding="utf-8"):
                targets.append(("README.md", readme_path))
        except Exception:
            pass

    missing = []
    for label, path in targets:
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        if install_cmd and install_cmd not in text:
            missing.append(f"{label} does not mention install command: {install_cmd}")

    check.details["missing"] = missing
    if missing:
        check.status = "warning"
        check.warnings = missing
    else:
        check.status = "passed"
    report.add_check(check)


def check_agent_context(project_path: Path, report: ValidationReport) -> None:
    """Check that AGENTS.md defines valid agent configurations."""
    check = ValidationCheck(
        "agent-context",
        "Verify AGENTS.md contains valid agent configurations",
    )

    agents_path = project_path / "AGENTS.md"
    if not agents_path.exists():
        check.status = "failed"
        check.errors = ["AGENTS.md not found"]
        report.add_check(check)
        return

    try:
        text = agents_path.read_text(encoding="utf-8")
    except Exception:
        check.status = "failed"
        check.errors = ["Cannot read AGENTS.md"]
        report.add_check(check)
        return

    agent_ids = re.findall(r"^### \[[^\]]+\]\(id: \x60([^\x60]+)\x60\)", text, re.MULTILINE)

    # Check for permissions and file tags
    has_permissions = "permissions" in text or "write_files" in text
    has_file_tags = "file_tags" in text or "@agent" in text
    has_context_router = "context_router" in text or "router_order" in text

    check.details = {
        "has_permissions": has_permissions,
        "has_file_tags": has_file_tags,
        "has_context_router": has_context_router,
        "agent_ids": agent_ids,
    }

    issues = []
    if not agent_ids:
        issues.append("No agent definitions found")
    if not has_permissions:
        issues.append("No agent permissions defined")
    if not has_file_tags:
        issues.append("No file tags defined for agents")
    if not has_context_router:
        issues.append("No context router configuration found")

    if issues:
        check.status = "warning"
        check.warnings = issues
    else:
        check.status = "passed"

    report.add_check(check)


def check_syntax(project_path: Path, report: ValidationReport) -> None:
    """Check syntax of generated files."""
    check = ValidationCheck(
        "syntax-validation",
        "Check syntax of generated YAML and JSON files",
    )

    syntax_errors = []
    files_checked = 0

    # Check YAML files
    yaml_files = [
        project_path / MANIFEST_PATH,
    ]
    for yf in yaml_files:
        if yf.exists():
            files_checked += 1
            try:
                parsed = load_yaml(yf)
                if not isinstance(parsed, dict) or "manifest" not in parsed:
                    syntax_errors.append(f"{yf.name}: missing manifest root")
            except Exception as e:
                syntax_errors.append(f"{yf.name}: {e}")

    # Check Markdown files for basic structure
    md_files = [
        project_path / "AGENTS.md",
        project_path / PROJECT_PROFILE_PATH,
        project_path / DESIGN_PATH,
        project_path / MEMORY_PATH,
        project_path / "README.md",
    ]
    for mf in md_files:
        if mf.exists():
            files_checked += 1
            try:
                text = mf.read_text(encoding="utf-8")
                generated_readme = mf.name == "README.md" and "AI Bootstrap" in text
                if len(text.strip()) == 0 and (mf.name != "README.md" or generated_readme):
                    syntax_errors.append(f"{mf.name}: empty file")
                if "{{" in text or "{%" in text:
                    if mf.name == "README.md" and not generated_readme:
                        continue
                    syntax_errors.append(f"{mf.name}: unresolved template markers")
                if mf.name == "PROJECT_PROFILE.md":
                    profile = _read_frontmatter(mf)
                    if "dna" not in profile:
                        syntax_errors.append(f"{mf.name}: missing dna frontmatter")
            except Exception as e:
                syntax_errors.append(f"{mf.name}: {e}")

    check.details = {
        "files_checked": files_checked,
        "syntax_errors": len(syntax_errors),
    }

    if syntax_errors:
        check.status = "failed"
        check.errors = syntax_errors
    else:
        check.status = "passed"

    report.add_check(check)


def check_adr_integrity(project_path: Path, report: ValidationReport) -> None:
    """Check that the ADR directory contains valid records."""
    check = ValidationCheck(
        "adr-integrity",
        "Verify ADR directory structure and content",
        severity="info",
    )

    adr_dir = project_path / ADR_DIR
    if not adr_dir.exists():
        check.status = "warning"
        check.warnings = ["docs/06-decisions/adr directory does not exist"]
        report.add_check(check)
        return

    adr_files = sorted(adr_dir.glob("*.md"))
    has_index = (project_path / ADR_INDEX_PATH).exists()
    has_first_adr = (project_path / INITIAL_ADR_PATH).exists()

    check.details = {
        "total_adr_files": len(adr_files),
        "has_index": has_index,
        "has_first_adr": has_first_adr,
    }

    issues = []
    if not has_index:
        issues.append("docs/06-decisions/adr/INDEX.md missing")
    if not has_first_adr:
        issues.append("No initial ADR record found")

    if issues:
        check.status = "warning"
        check.warnings = issues
    else:
        check.status = "passed"

    report.add_check(check)


def check_directory_structure(project_path: Path, report: ValidationReport) -> None:
    """Check that the governance directory structure is correct."""
    check = ValidationCheck(
        "directory-structure",
        "Verify governance directory structure",
        severity="info",
    )

    required_dirs = [str(path) for path in REQUIRED_DIRECTORIES]
    missing_dirs = []
    for d in required_dirs:
        if not (project_path / d).exists():
            missing_dirs.append(d)

    check.details = {
        "required_dirs": required_dirs,
        "missing_dirs": missing_dirs,
    }

    if missing_dirs:
        check.status = "failed"
        check.errors = [f"Missing directory: {d}" for d in missing_dirs]
    else:
        check.status = "passed"

    report.add_check(check)


# ─── Runtime & Visual Baseline Checks ────────────────────────────────────────

def _package_deps(app_dir: Path) -> dict:
    """Return merged dependencies for an app package.json (best effort)."""
    import json as _json

    pkg = app_dir / "package.json"
    if not pkg.exists():
        return {}
    try:
        data = _json.loads(pkg.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    deps = data.get("dependencies", {}) or {}
    dev = data.get("devDependencies", {}) or {}
    merged = {}
    if isinstance(deps, dict):
        merged.update(deps)
    if isinstance(dev, dict):
        merged.update(dev)
    return merged


def _apps_of_kind(project_path: Path, dependency_name: str) -> list[Path]:
    """Return app dirs under apps/ whose package.json depends on dependency_name."""
    apps_dir = project_path / "apps"
    found = []
    if not apps_dir.is_dir():
        return found
    for app_dir in sorted(p for p in apps_dir.iterdir() if p.is_dir()):
        deps = _package_deps(app_dir)
        if dependency_name in deps:
            found.append(app_dir)
    return found


def check_nitro_route_layout(project_path: Path, report: ValidationReport) -> None:
    """Verify Nitro ≥2.13 standalone apps use root-level routes/ instead of server/."""
    check = ValidationCheck(
        "nitro-route-layout",
        "Verify Nitro ≥2.13 standalone apps use root-level routes/ (not legacy server/)",
    )

    nitro_apps = _apps_of_kind(project_path, "nitropack")
    if not nitro_apps:
        check.status = "skipped"
        check.details = {"nitro_apps": 0, "reason": "no nitro apps declared"}
        report.add_check(check)
        return

    issues = []
    details = []
    for app in nitro_apps:
        has_root_routes = (app / "routes").is_dir()
        has_old_server = (app / "server").is_dir()
        has_routes_entries = has_root_routes and any((app / "routes").iterdir())
        details.append({
            "app": app.name,
            "root_routes": has_root_routes,
            "old_server": has_old_server,
        })
        if has_old_server and not has_root_routes:
            issues.append(
                f"{app.name}: uses legacy server/ layout; move routes to root-level routes/ for Nitro ≥2.13"
            )
        elif not has_routes_entries:
            issues.append(f"{app.name}: no root-level routes/ with route handlers found")

    check.details = {"nitro_apps": len(nitro_apps), "apps": details}
    if issues:
        check.status = "failed"
        check.errors = issues
    else:
        check.status = "passed"
    report.add_check(check)


def check_demo_visual_baseline(project_path: Path, report: ValidationReport) -> None:
    """Verify Nuxt apps ship a demo visual baseline (theme/fonts/layout/components/seed)."""
    check = ValidationCheck(
        "demo-visual-baseline",
        "Verify Nuxt apps ship a demo visual baseline (theme entry, fonts, token css, layouts, empty-state, seed)",
        severity="warning",
    )

    nuxt_apps = _apps_of_kind(project_path, "nuxt")
    if not nuxt_apps:
        check.status = "skipped"
        check.details = {"nuxt_apps": 0, "reason": "no nuxt apps declared"}
        report.add_check(check)
        return

    issues = []
    details = []
    for app in nuxt_apps:
        app_src = app / "app"
        has = {
            "theme_entry": (app / "app.config.ts").exists() or (app_src / "app.config.ts").exists(),
            "fonts_plugin": (app_src / "plugins" / "fonts.ts").exists(),
            "css_tokens": False,
            "layouts": bool((app_src / "layouts").is_dir() and list((app_src / "layouts").glob("*.vue"))),
            "empty_state": (app_src / "components" / "EmptyState.vue").exists(),
            "seed_data": (app_src / "utils" / "seed.ts").exists(),
        }
        for css in (
            app_src / "assets" / "css" / "main.css",
            app / "assets" / "css" / "main.css",
            app_src / "assets" / "css" / "main.scss",
        ):
            if css.exists():
                text = css.read_text(encoding="utf-8", errors="replace")
                # 识别语义令牌：既接受 --mc-* / var(-- 老范式，也接受 design-token-spec 的
                # @theme static { --color-*: ... } 新范式（Nuxt UI v4 / Tailwind v4 官方写法）
                if (
                    "--mc-" in text
                    or "var(--" in text
                    or "@theme" in text
                    or re.search(r"--[a-zA-Z][a-zA-Z0-9-]*\s*:", text)
                ):
                    has["css_tokens"] = True
                    break

        core_keys = ("theme_entry", "fonts_plugin", "css_tokens", "layouts", "empty_state")
        missing = [k for k in core_keys if not has[k]]

        composables_dir = app_src / "composables"
        has_composables = bool(composables_dir.is_dir() and list(composables_dir.glob("*.ts")))
        if has_composables and not has["seed_data"]:
            missing.append("seed_data")

        details.append({"app": app.name, **has})
        if missing:
            issues.append(f"{app.name}: missing demo visual baseline parts: {', '.join(missing)}")

    check.details = {"nuxt_apps": len(nuxt_apps), "apps": details}
    if issues:
        check.status = "warning"
        check.warnings = issues
    else:
        check.status = "passed"
    report.add_check(check)


def check_build_artifacts(project_path: Path, report: ValidationReport) -> None:
    """Verify built artifacts include Nitro route chunks / Nuxt output when a build exists."""
    check = ValidationCheck(
        "build-artifacts",
        "Verify built artifacts exist (Nitro route chunks + Nuxt output)",
        severity="warning",
    )

    apps_dir = project_path / "apps"
    found = []
    if apps_dir.is_dir():
        for app in sorted(p for p in apps_dir.iterdir() if p.is_dir()):
            nitro_routes = app / ".output" / "server" / "chunks" / "routes"
            nuxt_out = app / ".output" / "public"
            if nitro_routes.is_dir() and any(nitro_routes.iterdir()):
                found.append(f"{app.name}: .output/server/chunks/routes ({len(list(nitro_routes.iterdir()))} chunk(s))")
            elif nuxt_out.is_dir():
                found.append(f"{app.name}: .output/public present")

    if not found:
        check.status = "skipped"
        check.details = {"reason": "no build artifacts found; run pnpm build before deployment"}
        report.add_check(check)
        return

    check.details = {"artifacts": found}
    check.status = "passed"
    report.add_check(check)



def check_framework_component_gate(project_path: Path, report: ValidationReport) -> None:
    """Enforce framework component gate: reject deprecated UI component names in generated source.

    Scans Nuxt UI app sources for deprecated component usages (e.g. UFormGroup → UFormField)
    registered in scripts/framework_gate.py. Prevents SSR-collapse / hydration-mismatch class bugs.
    """
    check = ValidationCheck(
        "framework-component-gate",
        "Reject deprecated UI component names in generated source (e.g. Nuxt UI v4 UFormGroup → UFormField)",
    )

    deprecated = {k: v for k, v in DEPRECATED_COMPONENTS.items() if k and v}
    if not deprecated:
        check.status = "skipped"
        check.details = {"reason": "no deprecated components registered"}
        report.add_check(check)
        return

    nuxt_ui_apps = _apps_of_kind(project_path, "@nuxt/ui")
    if not nuxt_ui_apps:
        check.status = "skipped"
        check.details = {"nuxt_ui_apps": 0, "reason": "no @nuxt/ui apps declared"}
        report.add_check(check)
        return

    source_dirs = ("app", "src", "components", "pages", "layouts", "composables", "plugins", "middleware", "utils")
    patterns = {
        dep: re.compile(r"<\s*" + re.escape(dep) + r"\b")
        for dep in deprecated
    }
    closing_patterns = {
        dep: re.compile(r"</\s*" + re.escape(dep) + r"\s*>")
        for dep in deprecated
    }

    issues = []
    files_scanned = 0
    app_details = []
    for app in nuxt_ui_apps:
        hits = []
        for src_dir in source_dirs:
            base = app / src_dir
            if not base.is_dir():
                continue
            for f in sorted(base.rglob("*")):
                if f.suffix not in {".vue", ".ts", ".tsx", ".js", ".jsx", ".mjs"}:
                    continue
                if any(part in {".nuxt", "node_modules", ".output", "dist"} for part in f.parts):
                    continue
                files_scanned += 1
                try:
                    lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
                except Exception:
                    continue
                for idx, line in enumerate(lines, start=1):
                    for dep, repl in deprecated.items():
                        if patterns[dep].search(line) or closing_patterns[dep].search(line):
                            hits.append(f"{f.relative_to(project_path)}:{idx}: 使用已废弃组件 `{dep}`，请改为 `{repl}`")
        app_details.append({"app": app.name, "deprecated_hits": len(hits)})
        issues.extend(hits)

    check.details = {
        "nuxt_ui_apps": len(nuxt_ui_apps),
        "files_scanned": files_scanned,
        "apps": app_details,
        "deprecated_registry": list(deprecated),
    }
    if issues:
        check.status = "failed"
        check.errors = issues
    else:
        check.status = "passed"
    report.add_check(check)


def check_ui_stack_conformance(project_path: Path, report: ValidationReport) -> None:
    """Dispatch UI-stack conformance checks for every declared UI library."""
    _check_nuxt_ui_conformance(project_path, report)
    _check_vant_conformance(project_path, report)


def _check_nuxt_ui_conformance(project_path: Path, report: ValidationReport) -> None:
    """Verify Nuxt UI apps follow the official Nuxt UI v4 / Tailwind v4 theming paradigm.

    Official starter paradigm (ui.nuxt.com / github.com/nuxt-ui-templates):
    - main.css: ``@import "tailwindcss" theme(static)`` + ``@import "@nuxt/ui"`` + ``@theme static``
      registering brand color scales (--color-brand-* / --color-accent-*), NOT legacy --mc-* tokens
    - package.json declares ``tailwindcss`` and the icon collections used by ``i-*`` icons
    - app.config.ts maps ``ui.colors`` (primary/secondary/accent/...) to semantic colors
    - nuxt.config.ts registers ``ui.theme.colors`` so custom colors generate full utilities
    - app/error.vue ships the official UApp + UError error page
    - app sources use semantic utility classes (bg-primary / text-muted / border-default),
      not inline color hacks or legacy --mc-* custom tokens
    """
    check = ValidationCheck(
        "ui-stack-conformance",
        "Verify Nuxt UI apps follow the official Nuxt UI v4 / Tailwind v4 theming paradigm (@import tailwindcss + @theme static + ui.colors + tailwindcss dep)",
    )

    nuxt_ui_apps = _apps_of_kind(project_path, "@nuxt/ui")
    if not nuxt_ui_apps:
        check.status = "skipped"
        check.details = {"nuxt_ui_apps": 0, "reason": "no @nuxt/ui apps declared"}
        report.add_check(check)
        return

    issues = []
    warnings = []
    details = []
    for app in nuxt_ui_apps:
        app_src = app / "app"
        css_text = ""
        for css in (
            app_src / "assets" / "css" / "main.css",
            app / "assets" / "css" / "main.css",
            app_src / "assets" / "css" / "main.scss",
            app / "assets" / "css" / "main.scss",
        ):
            if css.exists():
                css_text = css.read_text(encoding="utf-8", errors="replace")
                break

        deps = _package_deps(app)
        app_issues = []
        app_warnings = []

        # 1) official CSS entry
        if not css_text:
            app_issues.append(f"{app.name}: 缺少全局样式入口 app/assets/css/main.css（官方范式：@import \"tailwindcss\" + @import \"@nuxt/ui\"）")
        else:
            if '@import "tailwindcss"' not in css_text:
                app_issues.append(f"{app.name}: main.css 缺少官方 @import \"tailwindcss\"（Tailwind v4 未接入）")
            if '@import "@nuxt/ui"' not in css_text:
                app_issues.append(f"{app.name}: main.css 缺少官方 @import \"@nuxt/ui\"")
            if "@theme" not in css_text:
                app_issues.append(f"{app.name}: main.css 未使用官方 @theme static 注册品牌色阶（--color-*）")
            if "--mc-" in css_text:
                app_warnings.append(f"{app.name}: main.css 仍在使用遗留 --mc-* 自定义令牌，应迁移到 @theme static 的 --color-brand-* / --color-accent-*")
            if "prefers-color-scheme" in css_text:
                app_warnings.append(f"{app.name}: main.css 手写 prefers-color-scheme 覆盖，应由 Nuxt UI colorMode 管理")

        # 2) dependencies
        if "tailwindcss" not in deps:
            app_issues.append(f"{app.name}: package.json 缺少 tailwindcss 依赖（Nuxt UI v4 官方范式必需）")
        icon_pkgs = sorted(k for k in deps if k.startswith("@iconify-json/"))
        if not icon_pkgs:
            app_warnings.append(f"{app.name}: 未声明 @iconify-json/* 图标集（i-* 图标建议显式安装，如 @iconify-json/lucide）")

        # 3) app.config.ts theme entry
        app_config = ""
        for cfg in (app_src / "app.config.ts", app / "app.config.ts"):
            if cfg.exists():
                app_config = cfg.read_text(encoding="utf-8", errors="replace")
                break
        if not app_config:
            app_issues.append(f"{app.name}: 缺少 app/app.config.ts 主题入口")
        else:
            if "ui:" not in app_config or "colors:" not in app_config:
                app_issues.append(f"{app.name}: app.config.ts 未声明 ui.colors 语义色映射")
            elif "primary:" not in app_config:
                app_warnings.append(f"{app.name}: app.config.ts ui.colors 未声明 primary（将回退到默认 green）")
            if "brand" not in app_config:
                app_warnings.append(f"{app.name}: app.config.ts ui.colors 未使用品牌色（建议 primary: 'brand'，并在 @theme 注册 --color-brand-*）")

        # 4) nuxt.config.ts ui.theme.colors
        nuxt_config = ""
        nuxt_cfg_path = app / "nuxt.config.ts"
        if nuxt_cfg_path.exists():
            nuxt_config = nuxt_cfg_path.read_text(encoding="utf-8", errors="replace")
        if not nuxt_config:
            app_issues.append(f"{app.name}: 缺少 nuxt.config.ts")
        elif "ui:" not in nuxt_config or "theme:" not in nuxt_config or "colors:" not in nuxt_config:
            app_warnings.append(f"{app.name}: nuxt.config.ts 未注册 ui.theme.colors（自定义语义色不会生成完整工具类）")

        # 5) error.vue (official starter ships UApp + UError)
        if not (app_src / "error.vue").exists():
            app_warnings.append(f"{app.name}: 缺少 app/error.vue（官方 starter 标配 UApp + UError 错误页）")

        # 6) legacy --mc-* tokens / inline color hacks in sources
        hack_hits = []
        source_dirs = ("app", "src", "components", "pages", "layouts", "composables", "plugins", "middleware", "utils")
        for src_dir in source_dirs:
            base = app / src_dir
            if not base.is_dir():
                continue
            for f in sorted(base.rglob("*")):
                if f.suffix not in {".vue", ".ts", ".tsx", ".js", ".jsx", ".css", ".scss"}:
                    continue
                if any(part in {".nuxt", "node_modules", ".output", "dist"} for part in f.parts):
                    continue
                try:
                    text = f.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    continue
                for idx, line in enumerate(text.splitlines(), start=1):
                    if "--mc-" in line:
                        hack_hits.append(f"{f.relative_to(project_path)}:{idx}: 使用遗留 --mc-* 令牌，应改用语义工具类")
                    elif "style=" in line and re.search(r"(?:color|background|border-color|box-shadow)\s*:", line):
                        hack_hits.append(f"{f.relative_to(project_path)}:{idx}: 内联样式颜色 hack，应改用 bg-primary/text-muted/border-default 等语义工具类")
        if hack_hits:
            app_warnings.append(f"{app.name}: {len(hack_hits)} 处内联颜色/遗留令牌（见 details.hack_hits）")
            app_warnings.extend(hack_hits[:8])

        details.append({
            "app": app.name,
            "has_css_entry": bool(css_text),
            "has_tailwindcss_dep": "tailwindcss" in deps,
            "icon_sets": icon_pkgs,
            "has_error_vue": (app_src / "error.vue").exists(),
            "hack_hits": hack_hits[:20],
        })
        issues.extend(app_issues)
        warnings.extend(app_warnings)

    check.details = {
        "nuxt_ui_apps": len(nuxt_ui_apps),
        "apps": details,
        "required_deps": ["tailwindcss"],
        "official_pattern": "https://ui.nuxt.com/docs/getting-started/theming + github.com/nuxt-ui-templates",
    }
    if issues:
        check.status = "failed"
        check.errors = issues[:20]
        check.warnings = warnings[:20]  # failed 时也保留迁移建议等 warning
    elif warnings:
        check.status = "warning"
        check.warnings = warnings[:20]
    else:
        check.status = "passed"
    report.add_check(check)



def _check_vant_conformance(project_path: Path, report: ValidationReport) -> None:
    """Verify Vant 4 apps follow the official Vant 4 quickstart / vant-demo paradigm.

    Official paradigm (vant-ui.github.io/vant quickstart + github.com/vant-ui/vant-demo):
    - 常规用法（官方推荐）: src/main.ts 引入 'vant/lib/index.css' 全量样式 + app.use(Button) 按需注册组件（Tree Shaking 默认可用）
    - 按需用法（体积极致）: unplugin-vue-components + @vant/auto-import-resolver（VantResolver），不引入 vant/lib/index.css
    - 反模式: Vant 4 起移除 babel-plugin-import；禁止全量 css 与 VantResolver 混用
    - 主题: 700+ 个 --van-* CSS 变量；:root 全局覆盖 + <van-config-provider :theme-vars> 组件级
    - 函数式 API: showToast / showDialog 从 vant 直接导入
    """
    check = ValidationCheck(
        "ui-stack-conformance",
        "Verify Vant 4 apps follow the official Vant 4 quickstart paradigm (vant/lib/index.css + app.use() or VantResolver; no babel-plugin-import; --van-* tokens)",
    )

    vant_apps = _apps_of_kind(project_path, "vant")
    if not vant_apps:
        check.status = "skipped"
        check.details = {"vant_apps": 0, "reason": "no vant apps declared"}
        report.add_check(check)
        return

    issues = []
    warnings = []
    details = []
    for app in vant_apps:
        deps = _package_deps(app)
        app_src = app / "src"
        main_ts = app_src / "main.ts"
        main_text = main_ts.read_text(encoding="utf-8", errors="replace") if main_ts.exists() else ""
        vite_cfg = app / "vite.config.ts"
        vite_text = vite_cfg.read_text(encoding="utf-8", errors="replace") if vite_cfg.exists() else ""
        app_issues = []
        app_warnings = []

        has_full_css = "vant/lib/index.css" in main_text
        has_resolver = "VantResolver" in (vite_text + main_text)
        has_auto_import = any(
            k in deps for k in ("@vant/auto-import-resolver", "unplugin-vue-components", "unplugin-auto-import")
        )

        # 1) 官方引入范式（二选一，禁止混用）
        if not main_text:
            app_issues.append(f"{app.name}: 缺少 src/main.ts（Vant 官方范式入口）")
        elif not has_full_css and not (has_resolver and has_auto_import):
            app_issues.append(
                f"{app.name}: 未按 Vant 4 官方范式接入——常规用法需在 src/main.ts 引入 'vant/lib/index.css' 并 app.use(组件)，"
                "或按需用法配置 unplugin-vue-components + @vant/auto-import-resolver（VantResolver，不引入全量 css）"
            )
        elif has_full_css and has_resolver:
            app_issues.append(
                f"{app.name}: 全量 vant/lib/index.css 与 VantResolver 按需引入混用（反模式：组件重复注册、样式错乱）"
            )

        # 2) 反模式依赖
        if "babel-plugin-import" in deps:
            app_issues.append(f"{app.name}: 仍依赖 babel-plugin-import（Vant 4 起官方已移除，按 quickstart 二选一接入）")

        # 3) 主题令牌：--van-* CSS 变量（uni.scss / App.vue / main.ts）
        token_files = []
        for name in ("uni.scss", "App.vue", "main.ts"):
            f = app_src / name
            if f.exists() and "--van-" in f.read_text(encoding="utf-8", errors="replace"):
                token_files.append(name)
        if not token_files:
            app_warnings.append(
                f"{app.name}: 未定义 --van-* 设计令牌（Vant 主题定制应使用 700+ 个 --van-* CSS 变量：:root 全局覆盖或 van-config-provider theme-vars）"
            )

        # 4) 组件基线与函数式 API 使用
        sources_text = ""
        for src_dir in ("src", "components", "pages"):
            base = app / src_dir
            if not base.is_dir():
                continue
            for f in sorted(base.rglob("*.vue")):
                try:
                    sources_text += f.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    continue
        if "<van-" not in sources_text:
            app_warnings.append(f"{app.name}: 源码未使用 <van-* 组件（Vant 组件基线缺失）")
        if "van-config-provider" not in sources_text:
            app_warnings.append(f"{app.name}: 未使用 <van-config-provider>（组件级主题定制建议 :theme-vars）")
        if "showToast" not in sources_text and "showDialog" not in sources_text:
            app_warnings.append(f"{app.name}: 未使用 Vant 函数式 API（showToast / showDialog）")

        details.append({
            "app": app.name,
            "has_full_css": has_full_css,
            "has_resolver": has_resolver,
            "has_auto_import_deps": has_auto_import,
            "token_files": token_files,
            "uses_van_components": "<van-" in sources_text,
            "uses_config_provider": "van-config-provider" in sources_text,
            "uses_functional_api": "showToast" in sources_text or "showDialog" in sources_text,
        })
        issues.extend(app_issues)
        warnings.extend(app_warnings)

    check.details = {
        "vant_apps": len(vant_apps),
        "apps": details,
        "official_pattern": "https://vant-ui.github.io/vant/#/zh-CN/quickstart + github.com/vant-ui/vant-demo",
    }
    if issues:
        check.status = "failed"
        check.errors = issues[:20]
        check.warnings = warnings[:20]
    elif warnings:
        check.status = "warning"
        check.warnings = warnings[:20]
    else:
        check.status = "passed"
    report.add_check(check)



# ─── Auto Fix ─────────────────────────────────────────────────────────────────

def auto_fix(project_path: Path, report: ValidationReport, quiet: bool = False) -> int:
    """Attempt to auto-fix identified issues. Returns number of fixes applied."""
    fixes_applied = 0

    # Fix missing bootstrap-manifest.yaml (simple version)
    manifest_path = project_path / MANIFEST_PATH
    if not manifest_path.exists():
        try:
            simple_manifest = f"""# bootstrap-manifest.yaml
# Auto-generated by AI Bootstrap Validation Engine

manifest:
  bootstrap_version: "{BOOTSTRAP_VERSION}"
  generated_at: "{datetime.now().isoformat()}"
  generated_by: "AI Bootstrap Validation Engine"
  project:
    name: "{project_path.name}"
  validation:
    status: "auto-fixed"
"""
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(simple_manifest, encoding="utf-8")
            fixes_applied += 1
            if not quiet:
                print(f"  🔧 Fixed: Created {MANIFEST_PATH}")
        except Exception:
            pass

    # Fix missing directory structure
    for dir_name in REQUIRED_DIRECTORIES:
        dir_path = project_path / dir_name
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                fixes_applied += 1
                if not quiet:
                    print(f"  🔧 Fixed: Created {dir_name}/ directory")
            except Exception:
                pass

    # Fix empty INDEX files
    index_files = {
        ADR_INDEX_PATH: "# ADR — 架构决策记录索引\n\n> 暂无 ADR 记录\n",
        DECISION_INDEX_PATH: "# 决策日志\n\n> 暂无决策记录\n",
        REVIEW_INDEX_PATH: "# 审查记录\n\n> 暂无审查记录\n",
        CURRENT_TASKS_PATH: "# 03 · Plans — 当前任务\n\n> 暂无活跃任务\n",
    }
    for rel_path, default_content in index_files.items():
        fpath = project_path / rel_path
        if not fpath.exists():
            try:
                fpath.parent.mkdir(parents=True, exist_ok=True)
                fpath.write_text(default_content, encoding="utf-8")
                fixes_applied += 1
                if not quiet:
                    print(f"  🔧 Fixed: Created {rel_path}")
            except Exception:
                pass

    return fixes_applied


# ─── Main Validation ──────────────────────────────────────────────────────────

def validate(project_dir: str, fix: bool = False, quiet: bool = False) -> ValidationReport:
    """Run all validation checks on the project directory."""
    project_path = Path(project_dir).resolve()

    if not project_path.exists():
        print(f"❌ Directory does not exist: {project_dir}", file=sys.stderr)
        sys.exit(1)

    report = ValidationReport(str(project_path))

    if not quiet:
        print(f"\n{'=' * 60}")
        print(f"  AI Bootstrap — Validation Engine v{BOOTSTRAP_VERSION}")
        print(f"{'=' * 60}")
        print(f"  Target: {project_path}")
        print()

    # Run all checks
    check_file_integrity(project_path, report)
    check_blueprint_consistency(project_path, report)
    check_dna_completeness(project_path, report)
    check_design_token_spec(project_path, report)
    check_project_layout(project_path, report)
    check_recommended_skills(project_path, report)
    check_agent_context(project_path, report)
    check_syntax(project_path, report)
    check_adr_integrity(project_path, report)
    check_directory_structure(project_path, report)
    check_nitro_route_layout(project_path, report)
    check_framework_component_gate(project_path, report)
    check_ui_stack_conformance(project_path, report)
    check_demo_visual_baseline(project_path, report)
    check_build_artifacts(project_path, report)

    # Compute score
    score = report.compute_score()
    status = report.get_status()

    # Auto-fix if requested
    fixes_applied = 0
    if fix and status == "failed":
        if not quiet:
            print("  🔧 Attempting auto-fix...")
        fixes_applied = auto_fix(project_path, report, quiet=quiet)
        if fixes_applied > 0:
            if not quiet:
                print(f"  ✅ Applied {fixes_applied} fixes")
            # Re-run checks after fix
            report = ValidationReport(str(project_path))
            check_file_integrity(project_path, report)
            check_blueprint_consistency(project_path, report)
            check_dna_completeness(project_path, report)
            check_design_token_spec(project_path, report)
            check_project_layout(project_path, report)
            check_recommended_skills(project_path, report)
            check_agent_context(project_path, report)
            check_syntax(project_path, report)
            check_adr_integrity(project_path, report)
            check_directory_structure(project_path, report)
            check_nitro_route_layout(project_path, report)
            check_framework_component_gate(project_path, report)
            check_ui_stack_conformance(project_path, report)
            check_demo_visual_baseline(project_path, report)
            check_build_artifacts(project_path, report)
            score = report.compute_score()
            status = report.get_status()

    if not quiet:
        status_icon = "✅" if status == "passed" else ("⚠️" if status == "warning" else "❌")
        print(f"\n  {status_icon} Validation {status.upper()} (Score: {score}/100)")
        print()

        for check in report.checks:
            icon = "✅" if check.status == "passed" else ("⚠️" if check.status == "warning" else "❌")
            print(f"  {icon} {check.name}")
            if check.errors:
                for err in check.errors:
                    print(f"       Error: {err}")
            if check.warnings:
                for warn in check.warnings:
                    print(f"       Warning: {warn}")

        print()
        print(f"  Summary: {report.summary['passed']} passed, "
              f"{report.summary['warnings']} warnings, "
              f"{report.summary['failures']} failures")
        print()

    return report


# ─── CLI Entry ────────────────────────────────────────────────────────────────

BOOTSTRAP_VERSION = "1.7.0"


def main():
    parser = argparse.ArgumentParser(
        description="AI Bootstrap — Validation Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 validate.py --dir ./my-project
  python3 validate.py --dir ./my-project --fix
  python3 validate.py --dir ./my-project --json
        """,
    )
    parser.add_argument("--dir", required=True, help="Target project directory")
    parser.add_argument("--fix", action="store_true", help="Auto-fix issues")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    report = validate(args.dir, fix=args.fix, quiet=args.json)

    status = report.get_status()

    if args.json:
        print(json.dumps(report.to_dict(), indent=2, default=str))
    else:
        # Print a compact summary
        print(f"Status: {status} | Score: {report.summary['score']}/100")
        print(f"Passed: {report.summary['passed']} | Warnings: {report.summary['warnings']} | Failures: {report.summary['failures']}")

    # Exit with status
    if status == "failed":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
