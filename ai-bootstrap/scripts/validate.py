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
from layout import (
    ADR_DIR,
    ADR_INDEX_PATH,
    CURRENT_TASKS_PATH,
    DECISION_INDEX_PATH,
    DESIGN_PATH,
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
        else:
            self.summary["failures"] += 1

    def compute_score(self) -> int:
        total = len(self.checks)
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
    ]
    for mf in md_files:
        if mf.exists():
            files_checked += 1
            try:
                text = mf.read_text(encoding="utf-8")
                if len(text.strip()) == 0:
                    syntax_errors.append(f"{mf.name}: empty file")
                if "{{" in text or "{%" in text:
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
  bootstrap_version: "1.0.0"
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
    check_agent_context(project_path, report)
    check_syntax(project_path, report)
    check_adr_integrity(project_path, report)
    check_directory_structure(project_path, report)

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
            check_agent_context(project_path, report)
            check_syntax(project_path, report)
            check_adr_integrity(project_path, report)
            check_directory_structure(project_path, report)
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

BOOTSTRAP_VERSION = "1.0.0"


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
