#!/usr/bin/env python3
"""
AI Bootstrap — Deep Detection Module v1.0

Enhanced library version and framework detection for --deep mode.
Imported by detect.py when --deep flag is set.

Usage:
    from deep_detect import deep_detect_project, deep_detect_config
"""

import re
from pathlib import Path


def read_file(path: Path) -> str:
    """Read a file safely, return empty string on failure."""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def is_node_package(text: str, pkg_name: str) -> bool:
    """Check if a package.json contains a specific dependency."""
    return bool(re.search(r'"' + re.escape(pkg_name) + r'":\s*"', text))


NODE_FW_MAP = [
    ("next", "next"), ("react", "react"), ("vue", "vue"),
    ("nuxt", "nuxt"), ("angular", "@angular/core"), ("svelte", "svelte"),
    ("solid", "solid-js"), ("remix", "@remix-run/react"),
]

NODE_BE_MAP = [
    ("nestjs", "@nestjs/core"), ("express", "express"),
    ("fastify", "fastify"), ("koa", "koa"),
    ("hono", "hono"), ("elysia", "elysia"),
]

NODE_TOOL_MAP = [
    ("prisma", "prisma"), ("drizzle", "drizzle-orm"),
    ("typeorm", "typeorm"), ("trpc", "@trpc/server"),
    ("authjs", "next-auth"), ("clerk", "@clerk/nextjs"),
    ("tailwindcss", "tailwindcss"), ("shadcn", "@radix-ui/react-slot"),
    ("zustand", "zustand"), ("jotai", "jotai"),
    ("msw", "msw"), ("playwright", "@playwright/test"),
    ("vitest", "vitest"), ("jest", "jest"),
]

PY_FW_MAP = [
    ("fastapi", "fastapi"), ("django", "django"),
    ("flask", "flask"), ("starlette", "starlette"),
    ("sanic", "sanic"), ("litestar", "litestar"),
]

PY_ML_MAP = [
    ("pytorch", "torch"), ("tensorflow", "tensorflow"),
    ("jax", "jax"), ("transformers", "transformers"),
    ("langchain", "langchain"), ("llamaindex", "llama-index"),
    ("openai", "openai"), ("anthropic", "anthropic"),
    ("haystack", "haystack-ai"),
]

PY_DATA_MAP = [
    ("pandas", "pandas"), ("numpy", "numpy"),
    ("polars", "polars"), ("duckdb", "duckdb"),
    ("sqlalchemy", "sqlalchemy"), ("alembic", "alembic"),
]

GO_FW_MAP = [
    ("gin", "gin-gonic/gin"), ("echo", "labstack/echo"),
    ("fiber", "gofiber/fiber"), ("chi", "go-chi/chi"),
    ("gorilla", "gorilla/mux"), ("grpc", "google.golang.org/grpc"),
    ("cobra", "spf13/cobra"), ("viper", "spf13/viper"),
    ("zap", "go.uber.org/zap"), ("zerolog", "rs/zerolog"),
    ("sqlx", "jmoiron/sqlx"), ("gorm", "gorm.io/gorm"),
    ("ent", "entgo.io/ent"), ("testify", "stretchr/testify"),
    ("mongo", "go.mongodb.org/mongo-driver"),
]

RUST_CRATE_MAP = [
    ("axum", "axum"), ("actix", "actix-web"),
    ("rocket", "rocket"), ("yew", "yew"),
    ("leptos", "leptos"), ("tokio", "tokio"),
    ("serde", "serde"), ("reqwest", "reqwest"),
    ("tower", "tower"), ("tonic", "tonic"),
    ("sqlx", "sqlx"), ("diesel", "diesel"),
    ("seaorm", "sea-orm"), ("tracing", "tracing"),
    ("clap", "clap"), ("anyhow", "anyhow"),
    ("thiserror", "thiserror"), ("bevy", "bevy"),
    ("tauri", "tauri"),
]


def deep_detect_nodejs(pkg_text: str, project_path: Path, lang_entry: dict) -> None:
    """Deep Node.js detection: lock files, 30+ frameworks/tools, exact versions."""
    frameworks = lang_entry.get("frameworks", {})

    # Detect all frameworks and tools from package.json
    for name, dep in NODE_FW_MAP + NODE_BE_MAP + NODE_TOOL_MAP:
        if is_node_package(pkg_text, dep):
            ver = None
            m = re.search(r'"' + re.escape(dep) + r'":\s*"([^"]+)"', pkg_text)
            if m:
                ver = m.group(1).replace("^", "").replace("~", "")
            frameworks[name] = ver or "detected"

    lang_entry["frameworks"] = frameworks

    # Parse lock file for exact resolved versions
    for lock_name in ["package-lock.json", "pnpm-lock.yaml", "yarn.lock"]:
        lock_file = project_path / lock_name
        if lock_file.exists():
            lock_text = read_file(lock_file)
            deep_info = lang_entry.get("deep", {})
            deep_info["lock_file"] = lock_name

            # Extract resolved versions from package-lock.json
            if lock_name == "package-lock.json":
                resolved = {}
                all_deps = NODE_FW_MAP + NODE_BE_MAP + NODE_TOOL_MAP
                for _, dep in all_deps:
                    # Pattern 1: "node_modules/depname": { "version": "x.y.z" }
                    pattern = r'"node_modules/' + re.escape(dep) + r'":\s*\{[^}]*"version":\s*"([^"]+)"'
                    m = re.search(pattern, lock_text)
                    if not m:
                        # Pattern 2: "depname": { "version": "x.y.z" }
                        pattern2 = r'"' + re.escape(dep) + r'":\s*\{[^}]*"version":\s*"([^"]+)"'
                        m = re.search(pattern2, lock_text)
                    if m:
                        resolved[dep] = m.group(1)
                if resolved:
                    deep_info["resolved_versions"] = resolved
            lang_entry["deep"] = deep_info
            break

    # Count installed node_modules packages
    nm_dir = project_path / "node_modules"
    if nm_dir.exists():
        count = len([d for d in nm_dir.iterdir() if d.is_dir() and not d.name.startswith(".")])
        lang_entry.setdefault("deep", {})
        lang_entry["deep"]["installed_count"] = count


def deep_detect_python(project_path: Path, lang_entry: dict) -> None:
    """Deep Python detection: ML/AI libs, data tools, lock files, notebooks."""
    # Check pyproject.toml
    py_text = read_file(project_path / "pyproject.toml")

    # Check requirements.txt
    req_text = read_file(project_path / "requirements.txt") or ""

    frameworks = lang_entry.get("frameworks", {})

    all_py_deps = PY_FW_MAP + PY_ML_MAP + PY_DATA_MAP

    for name, dep in all_py_deps:
        found = False
        ver = None

        # Check pyproject.toml
        if dep in py_text:
            found = True
            m = re.search(r'\b' + re.escape(dep) + r'\s*[=~>]+\s*"?([\d.]+)"?', py_text)
            if m:
                ver = m.group(1)

        # Check requirements.txt for exact version
        if not found and dep in req_text:
            found = True
            m = re.search(re.escape(dep) + r'==([\d.]+)', req_text)
            if m:
                ver = m.group(1)

        if found:
            frameworks[name] = ver or "detected"

    # Check Pipfile
    pipfile_text = read_file(project_path / "Pipfile") or ""
    for name, dep in all_py_deps:
        if dep in pipfile_text and dep not in str(frameworks):
            frameworks[name] = "detected"

    lang_entry["frameworks"] = frameworks

    # Parse lock files
    for lock_name in ["poetry.lock", "Pipfile.lock", "uv.lock"]:
        lock_file = project_path / lock_name
        if lock_file.exists():
            lang_entry.setdefault("deep", {})
            lang_entry["deep"]["lock_file"] = lock_name
            break

    # Count Jupyter notebooks
    nb_files = list(project_path.rglob("*.ipynb"))
    if nb_files:
        lang_entry.setdefault("deep", {})
        lang_entry["deep"]["jupyter_notebooks"] = len(nb_files)


def deep_detect_go(project_path: Path, lang_entry: dict) -> None:
    """Deep Go detection: go.sum parsing, go.mod scanning, 15+ libs."""
    frameworks = lang_entry.get("frameworks", {})

    # Scan .go files for imports (up to 50 files)
    go_files = list(project_path.rglob("*.go"))
    scanned = 0
    for f in go_files:
        if scanned >= 50:
            break
        content = read_file(f)
        for name, dep_path in GO_FW_MAP:
            if dep_path in content:
                frameworks[name] = "detected"
        scanned += 1

    # Parse go.sum for exact module versions
    go_sum = read_file(project_path / "go.sum")
    if go_sum:
        resolved = {}
        for line in go_sum.splitlines():
            parts = line.strip().split()
            if len(parts) >= 2:
                mod_name = parts[0]
                mod_ver = parts[1].replace("v", "").replace("/go.mod", "")
                for name, dep_path in GO_FW_MAP:
                    if dep_path in mod_name:
                        resolved[name] = mod_ver
        if resolved:
            lang_entry.setdefault("deep", {})
            lang_entry["deep"]["resolved_versions"] = resolved
            lang_entry["deep"]["lock_file"] = "go.sum"

    lang_entry["frameworks"] = frameworks


def deep_detect_rust(project_path: Path, lang_entry: dict) -> None:
    """Deep Rust detection: Cargo.lock parsing, 18+ crates."""
    cargo_text = read_file(project_path / "Cargo.toml")
    frameworks = lang_entry.get("frameworks", {})

    for name, dep in RUST_CRATE_MAP:
        if dep in cargo_text:
            frameworks[name] = "detected"

    # Parse Cargo.lock for exact versions
    cargo_lock = read_file(project_path / "Cargo.lock")
    if cargo_lock:
        resolved = {}
        current_name = None
        for line in cargo_lock.splitlines():
            s = line.strip()
            if s.startswith('name = "'):
                current_name = s.replace('name = "', "").replace('"', "")
            elif s.startswith('version = "') and current_name:
                ver = s.replace('version = "', "").replace('"', "")
                for name, dep in RUST_CRATE_MAP:
                    if dep == current_name:
                        resolved[name] = ver
                        break
                current_name = None
        if resolved:
            lang_entry.setdefault("deep", {})
            lang_entry["deep"]["resolved_versions"] = resolved
            lang_entry["deep"]["lock_file"] = "Cargo.lock"

    lang_entry["frameworks"] = frameworks


def deep_detect_cicd(project_path: Path, ci_list: list) -> None:
    """Deep CI/CD detection: parse workflow steps."""
    gh_workflows = project_path / ".github" / "workflows"
    if not gh_workflows.exists():
        return

    for wf_file in sorted(gh_workflows.glob("*.yml"))[:5]:
        wf_text = read_file(wf_file)
        if not wf_text:
            continue
        steps = set()
        for line in wf_text.splitlines():
            s = line.strip()
            if s.startswith("uses:"):
                steps.add(s.replace("uses:", "").strip())
            if "docker/build-push" in s:
                steps.add("docker-build")
            if "deploy" in s.lower():
                steps.add("deploy")
        if steps:
            for ci in ci_list:
                if ci.get("platform") == "github-actions":
                    ci.setdefault("steps", []).extend(list(steps))
                    ci["steps"] = list(set(ci["steps"]))


def deep_detect_docker(project_path: Path, docker: dict) -> None:
    """Deep Docker detection: base images, multi-stage, compose services."""
    base_images = []
    multi_stage = False

    for df_name in ["Dockerfile", "Dockerfile.dev", "Dockerfile.prod"]:
        df_path = project_path / df_name
        if df_path.exists():
            df_text = read_file(df_path)
            for line in df_text.splitlines():
                s = line.strip()
                if s.startswith("FROM "):
                    parts = s.replace("FROM ", "").split(" AS ")
                    image = parts[0].strip()
                    base_images.append(image)
                    if len(parts) > 1:
                        multi_stage = True

    if base_images:
        docker["base_images"] = base_images
    if multi_stage:
        docker["multi_stage"] = True

    # Parse docker-compose for services
    for dc_name in ["docker-compose.yml", "docker-compose.yaml"]:
        dc_path = project_path / dc_name
        if dc_path.exists():
            dc_text = read_file(dc_path)
            services = []
            for line in dc_text.splitlines():
                s = line.strip()
                if s.endswith(":") and not s.startswith(" ") and not s.startswith("#"):
                    svc_name = s.rstrip(":")
                    if svc_name not in ("services", "version", "networks", "volumes"):
                        services.append(svc_name)
            if services:
                docker["services"] = services


def deep_detect_env(project_path: Path) -> dict:
    """Deep environment detection: scan env files for variable names."""
    env_info = {}
    for env_file in [".env", ".env.example", ".env.local",
                     ".env.development", ".env.production"]:
        ef = project_path / env_file
        if ef.exists():
            env_text = read_file(ef)
            vars_found = []
            for line in env_text.splitlines():
                s = line.strip()
                if s and not s.startswith("#") and "=" in s:
                    var_name = s.split("=")[0].strip()
                    if var_name:
                        vars_found.append(var_name)
            if vars_found:
                env_info[env_file] = vars_found[:30]
    return env_info


def deep_scan_subprojects(project_path: Path) -> list[dict]:
    """Scan common monorepo directories for sub-projects.
    
    Checks packages/, apps/, services/, libs/, modules/ for:
    - go.mod → Go service
    - Cargo.toml → Rust service  
    - pyproject.toml / requirements.txt → Python service
    - package.json → Node.js package/app
    
    Returns list of {path, type, frameworks, deep} dicts.
    """
    subprojects = []
    scan_dirs = ["packages", "apps", "services", "libs", "modules"]
    
    for scan_dir in scan_dirs:
        base = project_path / scan_dir
        if not base.exists() or not base.is_dir():
            continue
        
        for item in sorted(base.iterdir()):
            if not item.is_dir() or item.name.startswith("."):
                continue
            
            sp = {
                "path": str(item.relative_to(project_path)),
                "type": None,
                "frameworks": {},
            }
            
            rel = str(item.relative_to(project_path))
            
            # 1. Go sub-project
            go_mod = item / "go.mod"
            if go_mod.exists():
                go_text = read_file(go_mod)
                frameworks = {}
                for name, dep in [
                    ("gin", "gin-gonic/gin"),
                    ("echo", "labstack/echo"),
                    ("fiber", "gofiber/fiber"),
                    ("chi", "go-chi/chi"),
                    ("gorilla", "gorilla/mux"),
                    ("grpc", "google.golang.org/grpc"),
                    ("cobra", "spf13/cobra"),
                    ("viper", "spf13/viper"),
                    ("zap", "go.uber.org/zap"),
                    ("zerolog", "rs/zerolog"),
                    ("sqlx", "jmoiron/sqlx"),
                    ("gorm", "gorm.io/gorm"),
                    ("ent", "entgo.io/ent"),
                    ("testify", "stretchr/testify"),
                    ("bun", "github.com/uptrace/bun"),
                ]:
                    if dep in go_text:
                        frameworks[name] = "detected"
                
                # go.sum resolved versions
                go_sum = read_file(item / "go.sum")
                resolved = {}
                if go_sum:
                    for line in go_sum.splitlines():
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            mod_ver = parts[1].replace("v", "").replace("/go.mod", "")
                            for name, dep in GO_FW_MAP:
                                if dep in parts[0]:
                                    resolved[name] = mod_ver
                
                sp["type"] = "go"
                sp["frameworks"] = frameworks
                if resolved:
                    sp["deep"] = {"resolved_versions": resolved, "lock_file": "go.sum"}
                subprojects.append(sp)
                continue
            
            # 2. Rust sub-project
            cargo = item / "Cargo.toml"
            if cargo.exists():
                cargo_text = read_file(cargo)
                frameworks = {}
                for name, dep in RUST_CRATE_MAP:
                    if dep in cargo_text:
                        frameworks[name] = "detected"
                
                cargo_lock = read_file(item / "Cargo.lock")
                resolved = {}
                if cargo_lock:
                    current_name = None
                    for line in cargo_lock.splitlines():
                        s = line.strip()
                        if s.startswith('name = "'):
                            current_name = s.replace('name = "', "").replace('"', "")
                        elif s.startswith('version = "') and current_name:
                            ver = s.replace('version = "', "").replace('"', "")
                            for name, dep in RUST_CRATE_MAP:
                                if dep == current_name:
                                    resolved[name] = ver
                                    break
                            current_name = None
                
                sp["type"] = "rust"
                sp["frameworks"] = frameworks
                if resolved:
                    sp["deep"] = {"resolved_versions": resolved, "lock_file": "Cargo.lock"}
                subprojects.append(sp)
                continue
            
            # 3. Python sub-project
            pyproject = item / "pyproject.toml"
            req = item / "requirements.txt"
            if pyproject.exists() or req.exists():
                py_text = read_file(pyproject) if pyproject.exists() else ""
                req_text = read_file(req) if req.exists() else ""
                
                frameworks = {}
                all_py_deps = PY_FW_MAP + PY_ML_MAP + PY_DATA_MAP
                for name, dep in all_py_deps:
                    if dep in py_text or dep in req_text:
                        frameworks[name] = "detected"
                
                nb_files = list(item.rglob("*.ipynb"))
                deep_info = {}
                if nb_files:
                    deep_info["jupyter_notebooks"] = len(nb_files)
                
                sp["type"] = "python"
                sp["frameworks"] = frameworks
                if deep_info:
                    sp["deep"] = deep_info
                subprojects.append(sp)
                continue
            
            # 4. Node.js sub-project
            pkg = item / "package.json"
            if pkg.exists():
                pkg_text = read_file(pkg)
                frameworks = {}
                all_node_deps = NODE_FW_MAP + NODE_BE_MAP + NODE_TOOL_MAP
                for name, dep in all_node_deps:
                    pattern = r'"' + re.escape(dep) + r'":\s*"([^"]+)"'
                    m = re.search(pattern, pkg_text)
                    if m:
                        ver = m.group(1).replace("^", "").replace("~", "")
                        frameworks[name] = ver or "detected"
                
                sp["type"] = "nodejs"
                sp["frameworks"] = frameworks
                subprojects.append(sp)
                continue
    
    return subprojects


# ─── Additional Language Deep Detection ──────────────────────────────────

def deep_detect_deno(project_path: Path) -> dict:
    """Deep Deno detection: import maps, deno.json config, lock files."""
    info = {}
    
    # Primary config file
    for df in ["deno.json", "deno.jsonc"]:
        df_path = project_path / df
        if df_path.exists():
            df_text = read_file(df_path)
            info["config_file"] = df
            
            # Check tasks
            if '"tasks"' in df_text or '"tasks":' in df_text:
                info["has_tasks"] = True
            
            # Check lock file
            if '"lock"' in df_text or '"lock":' in df_text:
                info["lock_configured"] = True
    
    # import_map.json
    im_path = project_path / "import_map.json"
    if im_path.exists():
        im_text = read_file(im_path)
        imports = []
        for line in im_text.splitlines():
            s = line.strip()
            if '"' in s and ":" in s and not s.startswith("{"):
                parts = s.split('"')
                for i, p in enumerate(parts):
                    if p and ":" in p and i > 0:
                        imports.append(parts[i-1].strip().strip('"'))
                        break
        if imports:
            info["imports"] = imports[:10]
    
    # deno.lock
    if (project_path / "deno.lock").exists():
        info["lock_file"] = "deno.lock"
    
    # Check for vendor directory
    if (project_path / "vendor").exists():
        info["vendor_dir"] = True
    
    return info


def deep_detect_flutter(project_path: Path) -> dict:
    """Deep Flutter/Dart detection: pubspec.lock, SDK version."""
    info = {}
    
    pubspec = read_file(project_path / "pubspec.yaml")
    if pubspec:
        # Extract SDK constraint
        m = re.search(r'sdk:\s*"([^"]+)"', pubspec)
        if m:
            info["sdk_constraint"] = m.group(1)
        
        # Check for Flutter
        if "flutter:" in pubspec or "flutter:" in pubspec:
            info["is_flutter"] = True
        
        # Count dependencies
        dep_count = 0
        in_deps = False
        for line in pubspec.splitlines():
            s = line.strip()
            if s == "dependencies:":
                in_deps = True
            elif s == "dev_dependencies:" or s.startswith("  ") == False:
                in_deps = False
            if in_deps and ":" in s and s.startswith("  "):
                dep_count += 1
        info["dependency_count"] = dep_count
    
    # pubspec.lock for exact versions
    lock = read_file(project_path / "pubspec.lock")
    if lock:
        info["lock_file"] = "pubspec.lock"
        packages = 0
        for line in lock.splitlines():
            if line.strip().startswith("  "):
                packages += 1
        info["packages_in_lock"] = packages
    
    return info


def deep_detect_swift(project_path: Path) -> dict:
    """Deep Swift detection: Package.swift dependencies."""
    info = {}
    
    swift_text = read_file(project_path / "Package.swift")
    if swift_text:
        # Detect package manager
        if "// swift-tools-version:" in swift_text:
            m = re.search(r'// swift-tools-version:\s*([\d.]+)', swift_text)
            if m:
                info["tools_version"] = m.group(1)
        
        # Count dependencies
        deps = []
        for line in swift_text.splitlines():
            s = line.strip()
            m = re.search(r'\.package\(url:\s*"([^"]+)"', s)
            if m:
                deps.append(m.group(1))
            m = re.search(r'\.package\(path:\s*"([^"]+)"', s)
            if m:
                deps.append("local:" + m.group(1))
        if deps:
            info["packages"] = deps[:10]
        
        # Detect Vapor
        if "vapor" in swift_text.lower():
            info["framework"] = "vapor"
    
    # Package.resolved for exact versions
    resolved = project_path / ".build" / "package.resolved"
    if resolved.exists():
        info["resolved"] = True
    
    return info


def deep_detect_kotlin(project_path: Path) -> dict:
    """Deep Kotlin detection: build.gradle.kts dependencies."""
    info = {}
    
    kts_text = read_file(project_path / "build.gradle.kts")
    if kts_text:
        # Kotlin version
        m = re.search(r'kotlin\(["\']jvm["\']\)\s*version\s*["\']([^"\']+)["\']', kts_text)
        if m:
            info["kotlin_version"] = m.group(1)
        
        m = re.search(r'kotlin\(["\']jvm["\']\)\s*version\s*["\']([^"\']+)["\']', kts_text)
        if not m:
            m = re.search(r'kotlin\(["\']jvm["\']\)', kts_text)
        
        # Dependencies
        deps = []
        for line in kts_text.splitlines():
            s = line.strip()
            m = re.search(r'implementation\(["\']([^:"\']+:[^"\']+)["\']\)', s)
            if m:
                deps.append(m.group(1))
        if deps:
            info["dependencies"] = deps[:15]
        
        # Detect Spring Boot
        if "spring" in kts_text.lower():
            info["framework"] = "spring-boot"
        elif "ktor" in kts_text.lower():
            info["framework"] = "ktor"
    
    # Gradle wrapper
    wrapper = project_path / "gradle" / "wrapper" / "gradle-wrapper.properties"
    if wrapper.exists():
        wrapper_text = read_file(wrapper)
        m = re.search(r'distributionUrl.*gradle-([\d.]+)', wrapper_text or "")
        if m:
            info["gradle_version"] = m.group(1)
    
    return info


# ─── Enhanced CI/CD Detection ────────────────────────────────────────────

def deep_detect_all_cicd(project_path: Path) -> list[dict]:
    """Detect all CI/CD platforms and parse their configs."""
    cicd_list = []
    
    # GitHub Actions (already detected, enhance with details)
    gh_dir = project_path / ".github" / "workflows"
    if gh_dir.exists():
        workflows = []
        for wf in sorted(gh_dir.glob("*.yml"))[:5]:
            wf_text = read_file(wf)
            if not wf_text:
                continue
            name = "unknown"
            for line in wf_text.splitlines():
                if line.strip().startswith("name:"):
                    name = line.split("name:")[1].strip()
                    break
            steps = set()
            for line in wf_text.splitlines():
                s = line.strip()
                if s.startswith("uses:"):
                    steps.add(s.replace("uses:", "").strip())
                if "docker/build-push" in s:
                    steps.add("docker-build")
                if "deploy" in s.lower():
                    steps.add("deploy")
            workflows.append({"name": name, "steps": list(steps) if steps else []})
        if workflows:
            cicd_list.append({"platform": "github-actions", "workflows": workflows})
    
    # GitLab CI
    gitlab_ci = project_path / ".gitlab-ci.yml"
    if gitlab_ci.exists():
        ci_text = read_file(gitlab_ci) or ""
        stages = set()
        jobs = []
        for line in ci_text.splitlines():
            s = line.strip()
            if s.startswith("- "):
                stages.add(s[2:].strip())
            if ":" in s and not s.startswith(" ") and not s.startswith(".") and not s.startswith("#"):
                job_name = s.split(":")[0].strip()
                if job_name not in ("stages", "image", "before_script", "after_script", "variables", "include", "cache", "default"):
                    jobs.append(job_name)
        cicd_list.append({
            "platform": "gitlab-ci",
            "jobs": jobs[:10],
            "stages": list(stages)[:10],
        })
    
    # CircleCI
    circle_dir = project_path / ".circleci"
    if circle_dir.exists():
        config = circle_dir / "config.yml"
        if config.exists():
            ci_text = read_file(config) or ""
            jobs = []
            for line in ci_text.splitlines():
                s = line.strip()
                if s.endswith(":") and not s.startswith(" ") and not s.startswith("#"):
                    job_name = s.rstrip(":")
                    if job_name not in ("version", "orbs", "executors", "commands", "jobs", "workflows"):
                        jobs.append(job_name)
            cicd_list.append({"platform": "circleci", "jobs": jobs[:10]})
    
    # Drone CI
    for drone_file in [".drone.yml", ".drone.jsonnet"]:
        if (project_path / drone_file).exists():
            cicd_list.append({"platform": "drone-ci", "config": drone_file})
            break
    
    # Jenkins
    if (project_path / "Jenkinsfile").exists():
        cicd_list.append({"platform": "jenkins", "config": "Jenkinsfile"})
    
    return cicd_list


# ─── Updated Subproject Scanner ──────────────────────────────────────────

def deep_scan_subprojects(project_path: Path) -> list[dict]:
    """Scan common monorepo directories for sub-projects.
    
    Checks packages/, apps/, services/, libs/, modules/ for:
    - go.mod → Go service
    - Cargo.toml → Rust service  
    - pyproject.toml / requirements.txt → Python service
    - package.json → Node.js package/app
    - deno.json / import_map.json → Deno project
    - pubspec.yaml → Flutter / Dart project
    - Package.swift → Swift project
    - build.gradle.kts → Kotlin project
    
    Returns list of {path, type, frameworks, deep} dicts.
    """
    subprojects = []
    scan_dirs = ["packages", "apps", "services", "libs", "modules"]
    
    for scan_dir in scan_dirs:
        base = project_path / scan_dir
        if not base.exists() or not base.is_dir():
            continue
        
        for item in sorted(base.iterdir()):
            if not item.is_dir() or item.name.startswith("."):
                continue
            
            sp = {
                "path": str(item.relative_to(project_path)),
                "type": None,
                "frameworks": {},
            }
            
            # ── Go ──
            if (item / "go.mod").exists():
                go_text = read_file(item / "go.mod")
                frameworks = {}
                for name, dep in [
                    ("gin", "gin-gonic/gin"), ("echo", "labstack/echo"),
                    ("fiber", "gofiber/fiber"), ("chi", "go-chi/chi"),
                    ("gorilla", "gorilla/mux"), ("grpc", "google.golang.org/grpc"),
                    ("cobra", "spf13/cobra"), ("viper", "spf13/viper"),
                    ("zap", "go.uber.org/zap"), ("zerolog", "rs/zerolog"),
                    ("sqlx", "jmoiron/sqlx"), ("gorm", "gorm.io/gorm"),
                    ("ent", "entgo.io/ent"), ("testify", "stretchr/testify"),
                    ("bun", "github.com/uptrace/bun"),
                ]:
                    if dep in go_text:
                        frameworks[name] = "detected"
                
                go_sum = read_file(item / "go.sum")
                resolved = {}
                if go_sum:
                    for line in go_sum.splitlines():
                        parts = line.strip().split()
                        if len(parts) >= 2 and len(parts[0]) > 2:
                            mod_ver = parts[1].replace("v", "").replace("/go.mod", "")
                            for name, dep in GO_FW_MAP:
                                if dep in parts[0]:
                                    resolved[name] = mod_ver
                
                sp["type"] = "go"
                sp["frameworks"] = frameworks
                if resolved:
                    sp["deep"] = {"resolved_versions": resolved, "lock_file": "go.sum"}
                subprojects.append(sp)
                continue
            
            # ── Rust ──
            if (item / "Cargo.toml").exists():
                cargo_text = read_file(item / "Cargo.toml")
                frameworks = {}
                for name, dep in RUST_CRATE_MAP:
                    if dep in cargo_text:
                        frameworks[name] = "detected"
                
                cargo_lock = read_file(item / "Cargo.lock")
                resolved = {}
                if cargo_lock:
                    current_name = None
                    for line in cargo_lock.splitlines():
                        s = line.strip()
                        if s.startswith('name = "'):
                            current_name = s.replace('name = "', "").replace('"', "")
                        elif s.startswith('version = "') and current_name:
                            ver = s.replace('version = "', "").replace('"', "")
                            for name, dep in RUST_CRATE_MAP:
                                if dep == current_name:
                                    resolved[name] = ver
                                    break
                            current_name = None
                
                sp["type"] = "rust"
                sp["frameworks"] = frameworks
                if resolved:
                    sp["deep"] = {"resolved_versions": resolved, "lock_file": "Cargo.lock"}
                subprojects.append(sp)
                continue
            
            # ── Python ──
            if (item / "pyproject.toml").exists() or (item / "requirements.txt").exists():
                py_text = read_file(item / "pyproject.toml") if (item / "pyproject.toml").exists() else ""
                req_text = read_file(item / "requirements.txt") if (item / "requirements.txt").exists() else ""
                frameworks = {}
                for name, dep in PY_FW_MAP + PY_ML_MAP + PY_DATA_MAP:
                    if dep in py_text or dep in req_text:
                        frameworks[name] = "detected"
                
                nb_files = list(item.rglob("*.ipynb"))
                deep_info = {"jupyter_notebooks": len(nb_files)} if nb_files else {}
                
                sp["type"] = "python"
                sp["frameworks"] = frameworks
                if deep_info:
                    sp["deep"] = deep_info
                subprojects.append(sp)
                continue
            
            # ── Node.js ──
            if (item / "package.json").exists():
                pkg_text = read_file(item / "package.json")
                frameworks = {}
                for name, dep in NODE_FW_MAP + NODE_BE_MAP + NODE_TOOL_MAP:
                    m = re.search(r'"' + re.escape(dep) + r'":\s*"([^"]+)"', pkg_text)
                    if m:
                        ver = m.group(1).replace("^", "").replace("~", "")
                        frameworks[name] = ver or "detected"
                
                sp["type"] = "nodejs"
                sp["frameworks"] = frameworks
                subprojects.append(sp)
                continue
            
            # ── Deno ──
            if (item / "deno.json").exists() or (item / "deno.jsonc").exists() or (item / "import_map.json").exists():
                sp["type"] = "deno"
                sp["deep"] = deep_detect_deno(item)
                subprojects.append(sp)
                continue
            
            # ── Flutter / Dart ──
            if (item / "pubspec.yaml").exists():
                sp["type"] = "flutter" if "flutter:" in (read_file(item / "pubspec.yaml") or "") else "dart"
                sp["deep"] = deep_detect_flutter(item)
                subprojects.append(sp)
                continue
            
            # ── Swift ──
            if (item / "Package.swift").exists():
                sp["type"] = "swift"
                sp["deep"] = deep_detect_swift(item)
                subprojects.append(sp)
                continue
            
            # ── Kotlin ──
            if (item / "build.gradle.kts").exists():
                sp["type"] = "kotlin"
                sp["deep"] = deep_detect_kotlin(item)
                subprojects.append(sp)
                continue
    
    return subprojects


# ─── Dockerfile AST Parser ──────────────────────────────────────────────

def parse_dockerfile_ast(filepath: Path) -> dict:
    """Parse a Dockerfile into a structured AST with stage analysis.
    
    Returns:
    {
        "path": "Dockerfile",
        "stages": [{ "name", "base_image", "instructions": [...] }],
        "analysis": { "multi_stage", "stage_count", "base_images",
                      "exposed_ports", "env_vars", "has_healthcheck",
                      "root_user", "uses_latest_tag", "copied_from_stages",
                      "workdir", "entrypoint", "package_managers" }
    }
    """
    if not filepath.exists():
        return {"path": filepath.name, "stages": [], "analysis": {}}
    
    text = read_file(filepath)
    if not text:
        return {"path": filepath.name, "stages": [], "analysis": {}}
    
    # Tokenize
    instructions = []
    current_lines = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        # Skip comments and empty lines
        if not line or line.startswith("#"):
            continue
        # Continuation: check if line ends with backslash
        if line.endswith("\\"):
            current_lines.append(line.rstrip("\\").strip())
            continue
        if current_lines:
            current_lines.append(line)
            full_line = " ".join(current_lines)
        else:
            full_line = line
        current_lines = []
        
        # Split into instruction type and arguments
        parts = full_line.split(None, 1)
        if len(parts) >= 1:
            instr_type = parts[0].upper()
            args = parts[1] if len(parts) > 1 else ""
            instructions.append({"type": instr_type, "args": args})
    
    # Group by stages (FROM lines start new stages)
    stages = []
    current_stage = None
    for instr in instructions:
        if instr["type"] == "FROM":
            current_stage = {"name": None, "base_image": None, "instructions": []}
            args = instr["args"]
            parts = args.split(" AS ")
            current_stage["base_image"] = parts[0].strip()
            if len(parts) > 1:
                current_stage["name"] = parts[1].strip()
            current_stage["instructions"].append(instr)
            stages.append(current_stage)
        elif current_stage is not None:
            current_stage["instructions"].append(instr)
    
    # Analysis
    analysis = {}
    
    # Multi-stage
    analysis["multi_stage"] = len(stages) > 1
    analysis["stage_count"] = len(stages)
    
    # Base images
    base_images = [s["base_image"] for s in stages if s["base_image"]]
    analysis["base_images"] = base_images
    
    # Image tagging analysis
    tags = []
    for img in base_images:
        if ":" in img:
            name, tag = img.split(":", 1)
            tags.append({"image": name, "tag": tag, "is_latest": tag == "latest"})
        else:
            tags.append({"image": img, "tag": "latest", "is_latest": True})
    analysis["image_tags"] = tags
    analysis["uses_latest_tag"] = any(t["is_latest"] for t in tags)
    analysis["uses_full_pinned"] = all(
        len(t["tag"].split(".")) >= 3 for t in tags if not t["is_latest"]
    ) if tags else False
    
    # Inter-stage dependencies (COPY --from=)
    copy_from = set()
    for stage in stages:
        for instr in stage["instructions"]:
            if instr["type"] in ("COPY", "ADD"):
                args = instr["args"]
                if "--from=" in args:
                    from_part = args.split("--from=")[1].split()[0].strip()
                    copy_from.add(from_part)
    analysis["copied_from_stages"] = list(copy_from) if copy_from else []
    
    # Stage dependency graph
    if len(stages) > 1:
        dep_graph = []
        for s in stages:
            for dep in analysis["copied_from_stages"]:
                if dep == s["name"]:
                    dep_graph.append({"from": s["name"] or s["base_image"], "to": "later_stages"})
        analysis["stage_dependencies"] = dep_graph
    
    # Exposed ports
    ports = []
    for stage in stages:
        for instr in stage["instructions"]:
            if instr["type"] == "EXPOSE":
                ports.extend(instr["args"].split())
    analysis["exposed_ports"] = list(set(ports))
    
    # Environment variables
    env_vars = {}
    for stage in stages:
        for instr in stage["instructions"]:
            if instr["type"] == "ENV":
                parts = instr["args"].split(None, 1)
                if len(parts) == 2:
                    env_vars[parts[0]] = parts[1]
                elif len(parts) == 1 and "=" in parts[0]:
                    k, v = parts[0].split("=", 1)
                    env_vars[k] = v
    analysis["env_vars"] = env_vars
    
    # Working directory
    workdir = None
    for stage in stages:
        for instr in stage["instructions"]:
            if instr["type"] == "WORKDIR":
                workdir = instr["args"]
    analysis["workdir"] = workdir
    
    # Entrypoint and default command
    cmd = None
    entrypoint = None
    for stage in stages:
        for instr in stage["instructions"]:
            if instr["type"] == "CMD":
                cmd = instr["args"]
            elif instr["type"] == "ENTRYPOINT":
                entrypoint = instr["args"]
    analysis["cmd"] = cmd
    analysis["entrypoint"] = entrypoint
    analysis["has_entrypoint"] = entrypoint is not None
    
    # HEALTHCHECK
    analysis["has_healthcheck"] = any(
        instr["type"] == "HEALTHCHECK"
        for stage in stages for instr in stage["instructions"]
    )
    
    # USER (root vs non-root security analysis)
    users_used = set()
    for stage in stages:
        for instr in stage["instructions"]:
            if instr["type"] == "USER":
                users_used.add(instr["args"].strip())
    analysis["root_user"] = len(users_used) == 0 or "root" in users_used
    analysis["users"] = list(users_used)
    
    # Package managers used (in RUN instructions)
    pkg_managers = set()
    for stage in stages:
        for instr in stage["instructions"]:
            if instr["type"] == "RUN":
                args = instr["args"].lower()
                if "apt-get" in args or "apt" in args:
                    pkg_managers.add("apt")
                if "apk" in args:
                    pkg_managers.add("apk")
                if "npm" in args or "yarn" in args or "pnpm" in args:
                    pkg_managers.add("npm")
                if "pip" in args or "pip3" in args:
                    pkg_managers.add("pip")
                if "cargo" in args:
                    pkg_managers.add("cargo")
                if "go install" in args or "go mod" in args:
                    pkg_managers.add("go")
    analysis["package_managers"] = list(pkg_managers) if pkg_managers else []
    
    # Layer count estimation
    total_instructions = sum(len(s["instructions"]) for s in stages)
    analysis["total_instructions"] = total_instructions
    analysis["estimated_layers"] = total_instructions  # Each instruction ≈ 1 layer
    
    return {"path": filepath.name, "stages": stages, "analysis": analysis}


def deep_detect_dockerfile(project_path: Path) -> dict:
    """Enhanced Dockerfile analysis: AST parsing across all Dockerfiles."""
    result = {"dockerfiles": [], "compose": {}}
    
    for df_name in ["Dockerfile", "Dockerfile.dev", "Dockerfile.prod",
                     "Dockerfile.test", "Dockerfile.staging"]:
        df_path = project_path / df_name
        if df_path.exists():
            ast = parse_dockerfile_ast(df_path)
            if ast.get("stages"):
                # Summarize for output
                analysis = ast.get("analysis", {})
                result["dockerfiles"].append({
                    "file": df_name,
                    "stages": analysis.get("stage_count", 0),
                    "base_images": analysis.get("base_images", []),
                    "multi_stage": analysis.get("multi_stage", False),
                    "ports": analysis.get("exposed_ports", []),
                    "env_vars": list(analysis.get("env_vars", {}).keys()),
                    "pkg_managers": analysis.get("package_managers", []),
                    "layers": analysis.get("estimated_layers", 0),
                    "root_user": analysis.get("root_user", True),
                    "has_healthcheck": analysis.get("has_healthcheck", False),
                    "entrypoint": analysis.get("entrypoint"),
                })
    
    # Parse docker-compose (enhanced)
    for dc_name in ["docker-compose.yml", "docker-compose.yaml"]:
        dc_path = project_path / dc_name
        if dc_path.exists():
            dc_text = read_file(dc_path)
            services = []
            current_service = None
            
            for line in dc_text.splitlines():
                s = line.strip()
                # Detect service name (key: at indentation level 0 or 2)
                indent = len(line) - len(line.lstrip())
                if indent == 0 and s.endswith(":") and not s.startswith("-"):
                    top_key = s.rstrip(":")
                    if top_key not in ("version", "services", "networks", "volumes", "configs", "secrets"):
                        continue
                elif indent == 2 and s.endswith(":"):
                    svc_name = s.rstrip(":")
                    if svc_name not in ("image", "build", "ports", "environment", "volumes",
                                        "depends_on", "networks", "restart", "command",
                                        "healthcheck", "env_file", "container_name",
                                        "networks", "dns", "dns_search", "tmpfs"):
                        current_service = {"name": svc_name, "image": None, "ports": [], "env_vars": []}
                        services.append(current_service)
                    else:
                        current_service = None
                elif indent == 4 and current_service:
                    if s.startswith("image:"):
                        current_service["image"] = s.split(":", 1)[1].strip()
                    elif s.startswith("build:"):
                        current_service["build"] = s.split(":", 1)[1].strip()
                    elif s.startswith("ports:"):
                        pass
                    elif ":" in s:
                        k, v = s.split(":", 1)
                        k = k.strip()
                        v = v.strip()
                        if k == "container_name":
                            current_service["container_name"] = v
                        elif k == "restart":
                            current_service["restart"] = v
            
            if services:
                result["compose"] = {
                    "file": dc_name,
                    "services": services,
                    "service_count": len(services),
                }
    
    return result


# ─── Enhanced CI/CD Deep Analyzer ──────────────────────────────────────

def parse_ci_trigger(line: str) -> dict:
    """Parse a CI trigger/on block into structured data."""
    s = line.strip().strip(",")
    result = {"event": s}
    if s.startswith("pull_request"):
        result["event"] = "pull_request"
    elif ":" in s and not s.startswith(" "):
        parts = s.split(":", 1)
        result["event"] = parts[0].strip()
        val = parts[1].strip().strip('"').strip("'")
        if val:
            result["value"] = val
    return result


def deep_detect_github_actions(gh_dir: Path) -> list[dict]:
    """Deep GitHub Actions workflow parser."""
    workflows = []
    for wf in sorted(gh_dir.glob("*.yml"))[:8]:
        wf_text = read_file(wf)
        if not wf_text:
            continue
        
        wf_info = {"file": wf.name, "name": "unknown", "on": [], "env": {}, "jobs": []}
        current_job = None
        in_on = False
        in_env = False
        in_job = False
        in_matrix = False
        indent_stack = []
        
        for line in wf_text.splitlines():
            stripped = line.strip()
            indent = len(line) - len(line.lstrip())
            
            if not stripped or stripped.startswith("#"):
                continue
            
            # Name
            if stripped.startswith("name:") and "name" not in [j.get("name") for j in wf_info["jobs"]]:
                val = stripped.split(":", 1)[1].strip().strip('"').strip("'")
                if not any(j.get("name") == val for j in wf_info.get("jobs", [])):
                    wf_info["name"] = val
                    in_on = False
                    in_env = False
                    continue
            
            # Trigger (on:)
            if stripped == "on:" or stripped.startswith("on: "):
                in_on = True
                in_env = False
                in_job = False
                trigger_val = stripped.split(":", 1)[1].strip() if ":" in stripped else ""
                if trigger_val:
                    for ev in trigger_v.split(","):
                        ev = ev.strip().strip("[]").strip().strip('"').strip("'")
                        if ev:
                            wf_info["on"].append(ev)
                    in_on = False
                continue
            
            if in_on:
                if indent == 0:
                    in_on = False
                elif indent == 2:
                    ev = stripped.rstrip(":")
                    if ev:
                        wf_info["on"].append(ev)
                    continue
            
            # Environment (env:)
            if stripped == "env:":
                in_on = False
                in_env = True
                in_job = False
                continue
            if in_env and indent == 2 and ":" in stripped:
                k, v = stripped.split(":", 1)
                wf_info["env"][k.strip()] = v.strip().strip('"').strip("'")
                continue
            if in_env and indent == 0 and stripped != "env:":
                in_env = False
            
            # Jobs
            if stripped.startswith("jobs:"):
                in_on = False
                in_env = False
                in_job = True
                continue
            
            if in_job:
                # Job name at indent 2
                if indent == 2 and stripped.endswith(":") and not stripped.startswith("-"):
                    job_name = stripped.rstrip(":")
                    if job_name not in ("strategy", "matrix", "with", "steps", "on",
                                        "services", "env", "needs", "runs-on"):
                        current_job = {
                            "name": job_name,
                            "runs_on": None,
                            "needs": [],
                            "steps": [],
                            "services": {},
                            "env": {},
                            "matrix": {},
                        }
                        wf_info["jobs"].append(current_job)
                    continue
                
                if current_job is None:
                    continue
                
                # runs-on
                if stripped.startswith("runs-on:"):
                    current_job["runs_on"] = stripped.split(":", 1)[1].strip().strip('"').strip("'")
                    continue
                
                # needs
                if stripped.startswith("needs:"):
                    needs_val = stripped.split(":", 1)[1].strip()
                    if needs_val:
                        for n in needs_val.replace("[", "").replace("]", "").split(","):
                            n = n.strip().strip('"').strip("'")
                            if n:
                                current_job["needs"].append(n)
                    continue
                
                # Strategy/matrix
                if stripped == "strategy:":
                    continue
                if indent == 4 and stripped.startswith("matrix:"):
                    in_matrix = True
                    continue
                if in_matrix and indent == 6 and ":" in stripped:
                    k, v = stripped.split(":", 1)
                    vals = v.strip().replace("[", "").replace("]", "")
                    current_job["matrix"][k.strip()] = [x.strip().strip('"').strip("'") for x in vals.split(",")]
                    continue
                if in_matrix and indent <= 4:
                    in_matrix = False
                
                # Services (service containers)
                if stripped == "services:":
                    continue
                if indent == 4 and stripped.endswith(":") and current_job.get("services") is not None:
                    svc_name = stripped.rstrip(":")
                    svc_info = {}
                    # Parse service image from next line
                    current_job["services"][svc_name] = svc_info
                    continue
                
                # Steps
                if stripped.startswith("- uses:") or stripped.startswith("- name:"):
                    step_info = {"uses": None, "name": None, "with": {}}
                    if stripped.startswith("- uses:"):
                        step_info["uses"] = stripped.split(":", 1)[1].strip()
                    elif stripped.startswith("- name:"):
                        step_info["name"] = stripped.split(":", 1)[1].strip().strip('"').strip("'")
                    current_job["steps"].append(step_info)
                    continue
                
                if stripped.startswith("- run:"):
                    run_cmd = stripped.split(":", 1)[1].strip()
                    current_job.setdefault("steps", []).append({"run": run_cmd})
                    continue
                
                # Step-level with/ env (simplified)
                if indent == 8 and stripped.startswith("with:") and current_job["steps"]:
                    current_job["steps"][-1]["with_block"] = True
                    continue
                if indent == 10 and ":" in stripped and current_job["steps"]:
                    k, v = stripped.split(":", 1)
                    if current_job["steps"][-1].get("with_block"):
                        current_job["steps"][-1].setdefault("with_params", {})
                        current_job["steps"][-1]["with_params"][k.strip()] = v.strip().strip('"').strip("'")
        
        if wf_info["jobs"] or wf_info["on"]:
            workflows.append(wf_info)
    
    return workflows


def deep_detect_cicd_deep(project_path: Path) -> dict:
    """Enhanced CI/CD deep analysis across all platforms.
    
    Returns structured CI/CD profile including:
    - All detected platforms with detailed configs
    - Aggregated analysis (total jobs, common patterns)
    """
    result = {"platforms": [], "analysis": {}}
    
    # GitHub Actions (deep)
    gh_dir = project_path / ".github" / "workflows"
    if gh_dir.exists():
        wf_results = deep_detect_github_actions(gh_dir)
        if wf_results:
            result["platforms"].append({
                "platform": "github-actions",
                "workflows": wf_results,
                "total_workflows": len(wf_results),
                "total_jobs": sum(len(w.get("jobs", [])) for w in wf_results),
            })
    
    # GitLab CI (deep)
    gl_path = project_path / ".gitlab-ci.yml"
    if gl_path.exists():
        gl_text = read_file(gl_path) or ""
        gl_info = {"platform": "gitlab-ci", "stages": [], "jobs": [], "variables": {}, "cache": {}, "services": []}
        
        current_job = None
        for line in gl_text.splitlines():
            s = line.strip()
            indent = len(line) - len(line.lstrip())
            
            if not s or s.startswith("#"):
                continue
            
            # Top-level keys
            if indent == 0 and s.endswith(":") and not s.startswith("."):
                key = s.rstrip(":")
                if key == "stages":
                    current_job = None
                elif key == "variables":
                    current_job = None
                elif key == "cache":
                    current_job = None
                elif key in ("default", "include", "image", "services"):
                    current_job = None
                else:
                    # Job definition
                    current_job = {"name": key, "stage": None, "script": [], "needs": [],
                                   "artifacts": {}, "cache": {}, "variables": {},
                                   "rules": [], "image": None, "services": [],
                                   "tags": [], "only": [], "except": []}
                    gl_info["jobs"].append(current_job)
            
            # Stages
            if s.startswith("- ") and 'stages' in line:
                gl_info["stages"].append(s[2:].strip())
            
            # Job details
            if current_job:
                if s.startswith("stage:"):
                    current_job["stage"] = s.split(":", 1)[1].strip()
                elif s.startswith("script:"):
                    current_job["script"].append("defined")
                elif s.startswith("- ") and current_job["script"] == ["defined"]:
                    current_job["script"].append(s[2:].strip())
                elif s.startswith("needs:"):
                    needs_val = s.split(":", 1)[1].strip()
                    if needs_val:
                        for n in needs_val.replace("[", "").replace("]", "").split(","):
                            n = n.strip().strip('"').strip("'")
                            if n:
                                current_job["needs"].append(n)
                elif s.startswith("image:"):
                    current_job["image"] = s.split(":", 1)[1].strip()
                elif s.startswith("tags:"):
                    pass
                elif s.startswith("only:"):
                    pass
                elif s.startswith("except:"):
                    pass
        
        result["platforms"].append(gl_info)
    
    # CircleCI (deep)  
    circle_config = project_path / ".circleci" / "config.yml"
    if circle_config.exists():
        ci_text = read_file(circle_config) or ""
        circle_info = {"platform": "circleci", "version": "2.1", "orbs": [], "executors": [], "jobs": [], "workflows": []}
        
        current_job = None
        for line in ci_text.splitlines():
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            
            if s.endswith(":") and not s.startswith(" "):
                key = s.rstrip(":")
                if key == "orbs":
                    pass
                elif key == "executors":
                    pass
                elif key == "jobs":
                    current_job = None
                elif key == "workflows":
                    current_job = None
                elif key in ("version", "setup"):
                    pass
                else:
                    pass
        
        result["platforms"].append(circle_info)
    
    # Drone CI
    for drone_file in [".drone.yml", ".drone.jsonnet"]:
        if (project_path / drone_file).exists():
            result["platforms"].append({"platform": "drone-ci", "config_file": drone_file})
            break
    
    # Jenkins
    if (project_path / "Jenkinsfile").exists():
        jk_text = read_file(project_path / "Jenkinsfile") or ""
        jk_info = {"platform": "jenkins", "stages": []}
        for line in jk_text.splitlines():
            s = line.strip()
            if s.startswith("stage(") or s.startswith("stage ("):
                m = re.search(r"stage\s*\(\s*['\"]([^'\"]+)['\"]", s)
                if m:
                    jk_info["stages"].append(m.group(1))
        if jk_info["stages"]:
            jk_info["stage_count"] = len(jk_info["stages"])
        result["platforms"].append(jk_info)
    
    # Aggregated analysis
    total_workflows = 0
    total_jobs = 0
    patterns = set()
    
    for p in result["platforms"]:
        plat = p.get("platform", "")
        if plat == "github-actions":
            total_workflows += p.get("total_workflows", len(p.get("workflows", [])))
            for w in p.get("workflows", []):
                for j in w.get("jobs", []):
                    total_jobs += 1
                    for s in j.get("steps", []):
                        step_text = str(s)
                        if "test" in step_text.lower():
                            patterns.add("test")
                        if "build" in step_text.lower():
                            patterns.add("build")
                        if "deploy" in step_text.lower():
                            patterns.add("deploy")
                        if "lint" in step_text.lower():
                            patterns.add("lint")
                        if "docker" in step_text.lower():
                            patterns.add("docker")
        elif plat == "gitlab-ci":
            total_jobs += len(p.get("jobs", []))
            for j in p.get("jobs", []):
                stage = j.get("stage", "")
                if stage:
                    patterns.add(stage)
    
    result["analysis"] = {
        "total_platforms": len(result["platforms"]),
        "total_workflows": total_workflows,
        "total_jobs": total_jobs,
        "cicd_patterns": sorted(patterns),
    }
    
    return result
