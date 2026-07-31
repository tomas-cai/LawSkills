#!/usr/bin/env python3
"""
AI Bootstrap — Project Detection Engine v1.0

Detects project environment, existing project structure, and technology stack.
Outputs a structured DetectionResult for downstream consumption.

Usage:
    python3 detect.py --dir /path/to/project [--json] [--deep]
"""

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional
from deep_detect import (
    deep_detect_nodejs, deep_detect_python, deep_detect_go,
    deep_detect_rust, deep_detect_cicd, deep_detect_docker,
    deep_detect_env, deep_scan_subprojects, deep_detect_deno,
    deep_detect_flutter, deep_detect_swift, deep_detect_kotlin,
    deep_detect_all_cicd, deep_detect_dockerfile,
    deep_detect_cicd_deep, parse_dockerfile_ast,
)


# ─── Data Models ──────────────────────────────────────────────────────────────

@dataclass
class RuntimeInfo:
    name: str
    version: Optional[str]
    path: Optional[str]


@dataclass
class FrameworkInfo:
    name: str
    version: Optional[str]


@dataclass
class LanguageInfo:
    name: str
    version: Optional[str]
    frameworks: dict = field(default_factory=dict)


@dataclass
class PackageManagerInfo:
    name: str
    version: Optional[str]


@dataclass
class MonorepoInfo:
    tool: Optional[str]
    packages: list = field(default_factory=list)


@dataclass
class DetectionResult:
    project_dir: str
    is_empty: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Environment
    environment: dict = field(default_factory=lambda: {
        "os": None, "os_version": None, "shell": None,
        "runtimes": [], "tools": [],
    })

    # Project
    project: dict = field(default_factory=lambda: {
        "type": None,  # monorepo | single | empty
        "languages": [],
        "package_managers": [],
        "monorepo": None,
    })

    # Repository
    repository: dict = field(default_factory=lambda: {
        "git": False, "branch": None, "remote": None,
        "ci_cd": [], "docker": {},
    })

    # Configuration
    config: dict = field(default_factory=lambda: {
        "eslint": False, "prettier": False, "typescript": False,
        "test_framework": None,
    })

    # Files
    key_files: list = field(default_factory=list)

    # Detection metadata
    detection: dict = field(default_factory=lambda: {
        "confidence": 0.0, "auto_detected_pct": 0, "warnings": [],
    })

    # Deep detection details (populated only in --deep mode)
    deep: dict = field(default_factory=dict)


# ─── Detection Helpers ────────────────────────────────────────────────────────

def run_cmd(cmd: list, timeout: int = 5) -> Optional[str]:
    """Run a command and return stdout, or None on failure."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip() if result.returncode == 0 else None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def read_file(path: Path) -> Optional[str]:
    """Read a file safely."""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None


def parse_version_from_text(text: str) -> Optional[str]:
    """Extract version string from text using common patterns."""
    m = re.search(r'"version":\s*"([^"]+)"', text)
    if m:
        return m.group(1)
    m = re.search(r'version\s*=\s*["\']([^"\']+)["\']', text)
    if m:
        return m.group(1)
    m = re.search(r'(\d+\.\d+\.\d+)', text)
    if m:
        return m.group(1)
    return None


# ─── Detectors ────────────────────────────────────────────────────────────────

def detect_environment(result: DetectionResult) -> None:
    """Detect OS, runtimes, and system tools."""
    env = result.environment

    # OS
    uname = run_cmd(["uname", "-s"])
    env["os"] = uname.lower() if uname else "unknown"
    env["os_version"] = run_cmd(["uname", "-r"])
    env["shell"] = os.environ.get("SHELL", "unknown")

    # Runtimes
    runtimes_map = {
        "node": ["node", "--version"],
        "python": ["python3", "--version"],
        "java": ["java", "-version"],
        "go": ["go", "version"],
        "rust": ["rustc", "--version"],
        "dotnet": ["dotnet", "--version"],
        "php": ["php", "--version"],
        "ruby": ["ruby", "--version"],
        "deno": ["deno", "--version"],
        "bun": ["bun", "--version"],
        "flutter": ["flutter", "--version"],
        "dart": ["dart", "--version"],
        "kotlin": ["kotlin", "-version"],
        "swift": ["swift", "--version"],
    }

    runtimes = []
    for name, cmd in runtimes_map.items():
        output = run_cmd(cmd)
        if output:
            # Extract first version-like segment
            ver_match = re.search(r'(\d+\.\d+[.\d]*)', output)
            version = ver_match.group(1) if ver_match else None
            # Find path
            which = run_cmd(["which", cmd[0]]) if cmd[0] != "python3" else run_cmd(["which", "python3"])
            runtimes.append(RuntimeInfo(name=name, version=version, path=which))
    env["runtimes"] = [asdict(r) for r in runtimes]

    # Tools
    tools_map = {
        "git": ["git", "--version"],
        "docker": ["docker", "--version"],
        "docker-compose": ["docker", "compose", "version"],
    }
    tools = []
    for name, cmd in tools_map.items():
        output = run_cmd(cmd)
        if output:
            ver_match = re.search(r'(\d+\.\d+[.\d]*)', output)
            tools.append({"name": name, "version": ver_match.group(1) if ver_match else None})
    env["tools"] = tools


def is_node_package(text: str, pkg_name: str) -> bool:
    """Check if a package.json contains a specific dependency."""
    return bool(re.search(rf'"{re.escape(pkg_name)}":\s*"', text))


def detect_project(result: DetectionResult, project_path: Path, deep: bool) -> None:
    """Detect project type, languages, frameworks."""
    proj = result.project
    key_files = []
    languages = []

    # Check project type
    has_package_json = (project_path / "package.json").exists()
    has_pyproject = (project_path / "pyproject.toml").exists()
    has_go_mod = (project_path / "go.mod").exists()
    has_cargo = (project_path / "Cargo.toml").exists()
    has_setup_py = (project_path / "setup.py").exists()
    has_requirements = (project_path / "requirements.txt").exists()
    has_pom = (project_path / "pom.xml").exists()
    has_gradle = (project_path / "build.gradle").exists()
    has_composer = (project_path / "composer.json").exists()
    has_gemfile = (project_path / "Gemfile").exists()
    has_csproj = list(project_path.glob("*.csproj")) if project_path.exists() else []
    has_deno_json = (project_path / "deno.json").exists() or (project_path / "deno.jsonc").exists() or (project_path / "import_map.json").exists()
    has_bun_lock = (project_path / "bun.lock").exists() or (project_path / "bunfig.toml").exists()
    has_pubspec = (project_path / "pubspec.yaml").exists()
    has_package_swift = (project_path / "Package.swift").exists()
    has_kotlin_gradle = (project_path / "build.gradle.kts").exists()

    # Deno
    if has_deno_json:
        deno_json_text = read_file(project_path / "deno.json") or read_file(project_path / "deno.jsonc") or ""
        deno_ver = None
        m = re.search(r'"version":\s*"([^"]+)"', deno_json_text)
        if m:
            deno_ver = m.group(1)
        frameworks = {}
        if "fresh" in deno_json_text:
            frameworks["fresh"] = "detected"
        if "oak" in deno_json_text:
            frameworks["oak"] = "detected"
        if "hono" in deno_json_text:
            frameworks["hono"] = "detected"
        if "deno_kv" in deno_json_text or "kv" in deno_json_text.lower():
            frameworks["deno_kv"] = "detected"
        languages.append({
            "name": "typescript",
            "runtime": "deno",
            "version": deno_ver or "latest",
            "frameworks": frameworks,
        })

    # Bun
    if has_bun_lock:
        languages.append({
            "name": "typescript",
            "runtime": "bun",
            "version": "latest",
            "frameworks": {},
        })

    # Flutter / Dart
    if has_pubspec:
        pubspec_text = read_file(project_path / "pubspec.yaml") or ""
        dart_ver = None
        m = re.search(r'sdk:\s*">?=?([\d.]+)', pubspec_text)
        if m:
            dart_ver = m.group(1)
        frameworks = {}
        if "flutter:" in pubspec_text or "flutter:" in pubspec_text:
            frameworks["flutter"] = "detected"
        languages.append({
            "name": "dart",
            "runtime": "flutter" if "flutter:" in pubspec_text else "dart",
            "version": dart_ver or "3.x",
            "frameworks": frameworks,
        })

    # Swift
    if has_package_swift:
        swift_text = read_file(project_path / "Package.swift") or ""
        frameworks = {}
        if "vapor" in swift_text.lower():
            frameworks["vapor"] = "detected"
        if "swiftui" in swift_text.lower() or "SwiftUI" in swift_text:
            frameworks["swiftui"] = "detected"
        languages.append({
            "name": "swift",
            "version": "5.x",
            "frameworks": frameworks,
        })

    # Kotlin
    if has_kotlin_gradle:
        kts_text = read_file(project_path / "build.gradle.kts") or ""
        frameworks = {}
        if "spring" in kts_text.lower():
            frameworks["spring"] = "detected"
        if "ktor" in kts_text.lower():
            frameworks["ktor"] = "detected"
        if "kotlinx" in kts_text:
            frameworks["kotlinx"] = "detected"
        languages.append({
            "name": "kotlin",
            "version": "latest",
            "frameworks": frameworks,
        })

    # Package managers
    has_pnpm_workspace = (project_path / "pnpm-workspace.yaml").exists()
    has_turbo = (project_path / "turbo.json").exists()
    has_nx = (project_path / "nx.json").exists()
    has_lerna = (project_path / "lerna.json").exists()

    # ─── Detect Languages ───

    # Node.js / TypeScript
    if has_package_json:
        pkg_text = read_file(project_path / "package.json")
        node_version = None
        if pkg_text:
            # Detect node engine version
            m = re.search(r'"node":\s*"([^"]+)"', pkg_text)
            if m:
                node_version = m.group(1).replace("^", "").replace("~", "")

            if pkg_text and is_node_package(pkg_text, "typescript"):
                ts_version = None
                m = re.search(r'"typescript":\s*"([^"]+)"', pkg_text)
                if m:
                    ts_version = m.group(1).replace("^", "").replace("~", "")
                languages.append({
                    "name": "typescript",
                    "version": ts_version or node_version or "latest",
                    "frameworks": {},
                })
            else:
                languages.append({
                    "name": "javascript",
                    "version": node_version or "latest",
                    "frameworks": {},
                })

            # Deep detection: lock files, more frameworks, exact versions
            if pkg_text and deep:
                lang_entry = languages[-1]
                deep_detect_nodejs(pkg_text, project_path, lang_entry)

    # Python
    if has_pyproject or has_setup_py or has_requirements:
        py_version = None
        if has_pyproject:
            py_text = read_file(project_path / "pyproject.toml")
            if py_text:
                m = re.search(r'requires-python\s*=\s*["\']([^"\']+)["\']', py_text)
                if m:
                    py_version = m.group(1)

        frameworks = {}
        lang_entry = {
            "name": "python",
            "version": py_version or "3.x",
            "frameworks": frameworks,
        }
        if deep:
            deep_detect_python(project_path, lang_entry)
        languages.append(lang_entry)

    # Go
    if has_go_mod:
        go_text = read_file(project_path / "go.mod")
        go_version = None
        if go_text:
            m = re.search(r'go\s+(\d+\.\d+)', go_text)
            if m:
                go_version = m.group(1)

        frameworks = {}
        lang_entry = {
            "name": "go",
            "version": go_version or "1.x",
            "frameworks": frameworks,
        }
        if deep:
            deep_detect_go(project_path, lang_entry)
        languages.append(lang_entry)

    # Rust
    if has_cargo:
        cargo_text = read_file(project_path / "Cargo.toml")
        frameworks = {}
        lang_entry = {
            "name": "rust",
            "version": None,
            "frameworks": frameworks,
        }
        if cargo_text and deep:
            deep_detect_rust(project_path, lang_entry)
        languages.append(lang_entry)

    # Java
    if has_pom:
        languages.append({"name": "java", "version": None, "frameworks": {}})
    if has_gradle:
        languages.append({"name": "java", "version": None, "frameworks": {}})
    if has_csproj:
        languages.append({"name": "csharp", "version": None, "frameworks": {}})
    if has_composer:
        languages.append({"name": "php", "version": None, "frameworks": {}})
    if has_gemfile:
        languages.append({"name": "ruby", "version": None, "frameworks": {}})

    proj["languages"] = languages

    # ─── Detect Package Managers ───
    pkg_managers = []
    if has_package_json:
        pkg_text = read_file(project_path / "package.json") or ""
        if "pnpm" in pkg_text or has_pnpm_workspace:
            pkg_managers.append({"name": "pnpm", "version": None})
        elif "yarn" in pkg_text:
            pkg_managers.append({"name": "yarn", "version": None})
        else:
            pkg_managers.append({"name": "npm", "version": None})
    if has_pyproject:
        py_text = read_file(project_path / "pyproject.toml") or ""
        if "poetry" in py_text:
            pkg_managers.append({"name": "poetry", "version": None})
        elif "uv" in py_text:
            pkg_managers.append({"name": "uv", "version": None})
        else:
            pkg_managers.append({"name": "pip", "version": None})
    if has_go_mod:
        pkg_managers.append({"name": "go-modules", "version": None})
    if has_cargo:
        pkg_managers.append({"name": "cargo", "version": None})
    if has_composer:
        pkg_managers.append({"name": "composer", "version": None})
    if has_gemfile:
        pkg_managers.append({"name": "bundler", "version": None})
    if has_csproj:
        pkg_managers.append({"name": "nuget", "version": None})

    proj["package_managers"] = pkg_managers

    # ─── Detect Monorepo ───
    monorepo = None
    if has_turbo:
        monorepo = {"tool": "turbo", "packages": _detect_packages(project_path)}
    elif has_nx:
        monorepo = {"tool": "nx", "packages": _detect_packages(project_path)}
    elif has_lerna:
        monorepo = {"tool": "lerna", "packages": _detect_packages(project_path)}
    elif has_pnpm_workspace:
        monorepo = {"tool": "pnpm-workspace", "packages": _detect_packages(project_path)}
    elif has_package_json:
        pkg_text = read_file(project_path / "package.json") or ""
        if '"workspaces"' in pkg_text or '"workspaces":' in pkg_text:
            monorepo = {"tool": "npm-yarn-workspace", "packages": _detect_packages(project_path)}
    proj["monorepo"] = monorepo

    # ─── Determine project type ───
    if monorepo:
        proj["type"] = "monorepo"
    elif len(languages) > 0:
        proj["type"] = "single"
    else:
        proj["type"] = "empty"

    # ─── Key files ───
    all_files = list(project_path.iterdir()) if project_path.exists() else []
    key_files = sorted(
        [f.name for f in all_files if f.is_file() and not f.name.startswith(".")]
    )
    result.key_files = key_files


def _detect_packages(project_path: Path) -> list:
    """Detect package directories in a monorepo."""
    packages = []

    # Check common monorepo package directories
    for pkg_dir in ["packages", "apps", "services", "libs"]:
        p = project_path / pkg_dir
        if p.exists() and p.is_dir():
            for sub in sorted(p.iterdir()):
                if sub.is_dir() and not sub.name.startswith("."):
                    packages.append({"path": str(sub.relative_to(project_path))})

    # Also check workspaces defined in package.json
    pkg_text = read_file(project_path / "package.json") or ""
    ws_match = re.search(r'"workspaces":\s*\[([^\]]+)\]', pkg_text, re.DOTALL)
    if ws_match:
        ws_items = re.findall(r'"([^"]+)"', ws_match.group(1))
        for ws in ws_items:
            if "*" in ws:
                pattern = ws.replace("*", "*")
                matched = list(project_path.glob(pattern))
                for m in matched:
                    if m.is_dir() and {"path": str(m.relative_to(project_path))} not in packages:
                        packages.append({"path": str(m.relative_to(project_path))})

    return packages


def detect_repository(result: DetectionResult, project_path: Path) -> None:
    """Detect git, CI/CD, Docker."""
    repo = result.repository
    git_dir = project_path / ".git"

    # Git
    if git_dir.exists() or git_dir.is_dir():
        repo["git"] = True
        repo["branch"] = run_cmd(["git", "-C", str(project_path), "branch", "--show-current"])
        remote = run_cmd(["git", "-C", str(project_path), "remote", "get-url", "origin"])
        repo["remote"] = remote

    # CI/CD
    cicd = []
    gh_actions = project_path / ".github" / "workflows"
    if gh_actions.exists():
        cicd.append({"platform": "github-actions", "files": [f.name for f in gh_actions.glob("*.yml")]})

    gitlab_ci = project_path / ".gitlab-ci.yml"
    if gitlab_ci.exists():
        cicd.append({"platform": "gitlab-ci", "files": [".gitlab-ci.yml"]})

    jenkins = project_path / "Jenkinsfile"
    if jenkins.exists():
        cicd.append({"platform": "jenkins", "files": ["Jenkinsfile"]})

    circle = project_path / ".circleci"
    if circle.exists():
        cicd.append({"platform": "circleci", "files": [f.name for f in circle.glob("config.yml")]})

    repo["ci_cd"] = cicd

    # Docker
    docker = {}
    if (project_path / "Dockerfile").exists():
        docker["dockerfile"] = True
    if (project_path / "docker-compose.yml").exists() or (project_path / "docker-compose.yaml").exists():
        docker["compose"] = True
    if (project_path / ".dockerignore").exists():
        docker["dockerignore"] = True
    repo["docker"] = docker


def detect_config(result: DetectionResult, project_path: Path, deep: bool) -> None:
    """Detect project configuration files and tools."""
    cfg = result.config
    cfg["eslint"] = (project_path / ".eslintrc.js").exists() or \
                    (project_path / ".eslintrc.json").exists() or \
                    (project_path / ".eslintrc.yaml").exists() or \
                    (project_path / "eslint.config.js").exists() or \
                    (project_path / "eslint.config.mjs").exists()
    cfg["prettier"] = (project_path / ".prettierrc").exists() or \
                      (project_path / ".prettierrc.json").exists() or \
                      (project_path / ".prettierrc.js").exists() or \
                      (project_path / "prettier.config.js").exists()
    cfg["typescript"] = (project_path / "tsconfig.json").exists()

    # Test frameworks
    if (project_path / "vitest.config.ts").exists() or (project_path / "vitest.config.js").exists():
        cfg["test_framework"] = "vitest"
    elif (project_path / "jest.config.js").exists() or (project_path / "jest.config.ts").exists():
        cfg["test_framework"] = "jest"
    elif (project_path / "pytest.ini").exists() or (project_path / "conftest.py").exists():
        cfg["test_framework"] = "pytest"
    elif (project_path / "Cargo.toml").exists():
        cfg["test_framework"] = "cargo-test"

    # Deep config detection
    if deep:
        # Build tools
        cfg["makefile"] = (project_path / "Makefile").exists() or (project_path / "makefile").exists()
        cfg["justfile"] = (project_path / "justfile").exists() or (project_path / "justfile").exists()
        cfg["docker_compose"] = (project_path / "docker-compose.yml").exists() or \
                                 (project_path / "docker-compose.yaml").exists()
        cfg["editor_config"] = (project_path / ".editorconfig").exists()

        # Go tools
        if (project_path / "go.mod").exists():
            if (project_path / "Taskfile.yml").exists() or (project_path / "Taskfile.yaml").exists():
                cfg["task_runner"] = "task"
            if (project_path / "Makefile").exists():
                cfg["build_tool"] = "make"
            else:
                cfg["build_tool"] = "go-build"

        # Rust tools
        if (project_path / "Cargo.toml").exists():
            cfg["build_tool"] = "cargo"
            if (project_path / ".cargo").exists() and (project_path / ".cargo" / "config.toml").exists():
                cfg["cargo_config"] = True

        # Python tools
        if (project_path / "pyproject.toml").exists():
            py_text = read_file(project_path / "pyproject.toml") or ""
            if "[tool.poetry]" in py_text:
                cfg["python_build"] = "poetry"
            elif "[build-system]" in py_text and "hatchling" in py_text:
                cfg["python_build"] = "hatch"
            elif "[tool.setuptools]" in py_text:
                cfg["python_build"] = "setuptools"
            else:
                cfg["python_build"] = "setuptools"
            # Ruff
            if "[tool.ruff]" in py_text:
                cfg["ruff"] = True

        # TypeScript tools
        if cfg.get("typescript"):
            ts_text = read_file(project_path / "tsconfig.json") or ""
            if "strict" in ts_text:
                cfg["ts_strict"] = True
            if "jsx" in ts_text:
                cfg["ts_jsx"] = True


def compute_confidence(result: DetectionResult, project_path: Path) -> None:
    """Compute detection confidence score."""
    det = result.detection
    total_fields = 14
    detected_fields = 0

    # Environment fields
    if result.environment.get("os") and result.environment["os"] != "unknown":
        detected_fields += 1
    if result.environment.get("runtimes"):
        detected_fields += 1

    # Project fields
    proj = result.project
    if proj.get("type") and proj["type"] != "empty":
        detected_fields += 1
    if proj.get("languages"):
        detected_fields += 1
    if proj.get("package_managers"):
        detected_fields += 1

    # Repository fields
    repo = result.repository
    if repo.get("git"):
        detected_fields += 1
    if repo.get("ci_cd"):
        detected_fields += 1
    if repo.get("docker"):
        detected_fields += 1

    # Config fields
    cfg = result.config
    if cfg.get("eslint"):
        detected_fields += 1
    if cfg.get("prettier"):
        detected_fields += 1
    if cfg.get("typescript"):
        detected_fields += 1
    if cfg.get("test_framework"):
        detected_fields += 1

    # Key files
    if result.key_files:
        detected_fields += 1

    det["confidence"] = round(detected_fields / total_fields, 2)
    det["auto_detected_pct"] = round((detected_fields / total_fields) * 100)


# ─── Main Detection ───────────────────────────────────────────────────────────

def detect(project_dir: str, deep: bool = False) -> DetectionResult:
    """
    Run full detection on the given project directory.
    Returns a structured DetectionResult.
    """
    project_path = Path(project_dir).resolve()

    if not project_path.exists():
        print(f"❌ Directory does not exist: {project_dir}", file=sys.stderr)
        sys.exit(1)

    result = DetectionResult(
        project_dir=str(project_path),
        is_empty=not any(project_path.iterdir()) if project_path.exists() else True
    )

    # Phase 1: Environment
    detect_environment(result)

    # Phase 2: Project
    detect_project(result, project_path, deep)

    # Phase 3: Repository
    detect_repository(result, project_path)

    # Phase 4: Config
    detect_config(result, project_path, deep)

    # Phase 5: Docker deep analysis
    if deep:
        # Full Dockerfile AST analysis
        docker_ast = deep_detect_dockerfile(project_path)
        if docker_ast.get("dockerfiles") or docker_ast.get("compose"):
            result.repository["docker_ast"] = docker_ast
        deep_detect_cicd(project_path, result.repository.get("ci_cd", []))
        env_info = deep_detect_env(project_path)
        if env_info:
            result.deep["env_files"] = env_info
        
        # Additional ecosystem deep detection (Deno, Flutter, Swift, Kotlin)
        for lang in result.project.get("languages", []):
            lname = lang.get("name", "")
            lruntime = lang.get("runtime", "")
            if lruntime == "deno" or (lname == "typescript" and (project_path / "deno.json").exists()):
                result.deep["deno"] = deep_detect_deno(project_path)
            elif lname == "dart":
                result.deep["flutter_dart"] = deep_detect_flutter(project_path)
            elif lname == "swift":
                result.deep["swift"] = deep_detect_swift(project_path)
            elif lname == "kotlin":
                result.deep["kotlin"] = deep_detect_kotlin(project_path)
        
        # Enhanced CI/CD deep analysis
        cicd_deep = deep_detect_cicd_deep(project_path)
        if cicd_deep.get("platforms"):
            result.repository["cicd_deep"] = cicd_deep

    # Phase 6: Sub-project scanning (--deep only)
    if deep:
        subprojects = deep_scan_subprojects(project_path)
        if subprojects:
            result.project["subprojects"] = subprojects

    # Phase 7: Confidence
    compute_confidence(result, project_path)

    return result


def format_result(result: DetectionResult) -> str:
    """Format DetectionResult as human-readable string."""
    lines = []
    lines.append("=" * 60)
    lines.append("  AI Bootstrap — Project Detection Report")
    lines.append("=" * 60)
    lines.append(f"  Directory:  {result.project_dir}")
    lines.append(f"  Empty:      {'Yes' if result.is_empty else 'No'}")
    lines.append(f"  Confidence: {result.detection['confidence']:.0%}")
    lines.append("")

    # Project type
    proj = result.project
    lines.append(f"  Project Type: {proj.get('type', 'unknown')}")
    if proj.get("monorepo"):
        m = proj["monorepo"]
        lines.append(f"  Monorepo:     {m['tool']} ({len(m['packages'])} packages)")

    # Languages
    if proj.get("languages"):
        lines.append("")
        lines.append("  ── Languages ──")
        for lang in proj["languages"]:
            fw_text = ""
            if lang.get("frameworks"):
                fw_text = f" [{', '.join(lang['frameworks'].keys())}]"
            lines.append(f"    • {lang['name']} {lang.get('version', '')}{fw_text}")

    # Package managers
    if proj.get("package_managers"):
        lines.append("")
        lines.append("  ── Package Managers ──")
        for pm in proj["package_managers"]:
            lines.append(f"    • {pm['name']}")

    # Runtimes
    env = result.environment
    if env.get("runtimes"):
        lines.append("")
        lines.append("  ── Runtimes ──")
        for rt in env["runtimes"]:
            lines.append(f"    • {rt['name']} {rt.get('version', '')}")

    # Git
    repo = result.repository
    if repo.get("git"):
        lines.append("")
        lines.append(f"  Git:          {repo.get('branch', '?')}")
        if repo.get("remote"):
            lines.append(f"  Remote:       {repo['remote']}")
        if repo.get("ci_cd"):
            for ci in repo["ci_cd"]:
                lines.append(f"  CI/CD:        {ci['platform']} ({len(ci['files'])} workflows)")

    # Docker
    if repo.get("docker"):
        docker_items = [k for k, v in repo["docker"].items() if v]
        if docker_items:
            lines.append(f"  Docker:       {', '.join(docker_items)}")

    # Config
    cfg = result.config
    config_items = [k for k, v in cfg.items() if v and k != "test_framework"]
    if config_items:
        lines.append("")
        lines.append("  ── Config ──")
        lines.append(f"    • {', '.join(config_items)}")
        if cfg.get("test_framework"):
            lines.append(f"    • test: {cfg['test_framework']}")

    # Warnings
    if result.detection.get("warnings"):
        lines.append("")
        lines.append("  ⚠ Warnings:")
        for w in result.detection["warnings"]:
            lines.append(f"    • {w}")

    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


# ─── CLI Entry ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AI Bootstrap — Project Detection Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 detect.py --dir ./my-project
  python3 detect.py --dir ./my-project --json
  python3 detect.py --dir ./my-project --deep --json
        """,
    )
    parser.add_argument("--dir", required=True, help="Target project directory")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--deep", action="store_true", help="Deep detection (analyze file contents)")
    args = parser.parse_args()

    result = detect(args.dir, deep=args.deep)

    if args.json:
        print(json.dumps(asdict(result), indent=2, default=str))
    else:
        print(format_result(result))

    # Exit with status based on result
    if result.detection["confidence"] < 0.3:
        sys.exit(1)  # Low confidence
    sys.exit(0)


if __name__ == "__main__":
    main()
