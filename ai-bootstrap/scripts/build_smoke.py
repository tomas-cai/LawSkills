#!/usr/bin/env python3
"""
AI Bootstrap — Starter Build Smoke Checker v1.0

对生成项目里的 starter 做「真实安装 + 构建」冒烟：逐个 target 执行
`<pm> install`（除非 --skip-install）与构建脚本（build / build:h5 / build:prod 等），
输出每个 starter 的 install / build 状态表。用于验证「生成即能跑」，
避免瘦 DEMO starter 的依赖或构建配置在依赖升级后漂移。

与 smoke.py 的分工：
- smoke.py        运行期冒烟：启动服务后请求各应用端口（需先 build/dev 起来）
- build-smoke.py  构建期冒烟：真实 `pnpm install` + 构建，验证可安装、可构建

用法：
    python3 build-smoke.py --dir /path/to/project
    python3 build-smoke.py --dir /path/to/project --skip-install
    python3 build-smoke.py --dir /path/to/project --only frontend,apps/web
    python3 build-smoke.py --dir /path/to/project --plan          # 只打印计划不执行
    python3 build-smoke.py --dir /path/to/project --json
    python3 build-smoke.py --dir /path/to/project --timeout 900 --install-args "--offline"
"""

import argparse
import json
import shlex
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_TIMEOUT = 600  # 单条命令超时（秒）
OUTPUT_TAIL = 1600  # 输出截断字节数
SKIP_DIRS = {"node_modules", ".git", ".output", "dist", ".nuxt", ".next", "__pycache__", "target"}

# 构建脚本优先级：uni-app 用 build:h5，部分栈用 build:prod
BUILD_SCRIPT_PRIORITY = ("build", "build:h5", "build:prod", "build:h5:app", "build:mp-weixin")


def load_manifest(project_dir: Path) -> dict | None:
    """读取 .ai-bootstrap/bootstrap-manifest.yaml（无则返回 None）。"""
    manifest = project_dir / ".ai-bootstrap" / "bootstrap-manifest.yaml"
    if not manifest.exists():
        return None
    try:
        from yaml_utils import load_yaml

        return load_yaml(manifest)
    except Exception:  # noqa: BLE001
        return None


def manifest_targets(manifest: dict | None) -> list[dict]:
    """从 manifest 的 starter.template_dirs 读出 {starter, target} 列表。"""
    if not manifest:
        return []
    starter = (manifest.get("manifest") or {}).get("starter") or {}
    dirs = starter.get("template_dirs") or []
    out = []
    for spec in dirs:
        if isinstance(spec, dict) and spec.get("dir"):
            out.append({"starter": spec.get("dir"), "target": str(spec.get("target") or "")})
    return out


def _iter_pkg_dirs(root: Path, max_depth: int = 3):
    """遍历目录树（跳过 SKIP_DIRS），产出包含 package.json 的相对目录。"""
    stack = [(root, 0)]
    while stack:
        current, depth = stack.pop()
        if depth >= max_depth:
            continue
        try:
            children = sorted(current.iterdir(), key=lambda p: p.name)
        except OSError:
            continue
        for child in children:
            if not child.is_dir() or child.name in SKIP_DIRS:
                continue
            if (child / "package.json").exists():
                yield child.relative_to(root).as_posix()
            else:
                stack.append((child, depth + 1))


def _iter_maven_dirs(root: Path, max_depth: int = 3):
    """遍历目录树，产出包含 pom.xml 的相对目录（用于 Maven 构建目标）。"""
    stack = [(root, 0)]
    while stack:
        current, depth = stack.pop()
        if depth >= max_depth:
            continue
        try:
            children = sorted(current.iterdir(), key=lambda p: p.name)
        except OSError:
            continue
        for child in children:
            if not child.is_dir() or child.name in SKIP_DIRS:
                continue
            if (child / "pom.xml").exists():
                yield child.relative_to(root).as_posix()
            else:
                stack.append((child, depth + 1))


def scan_fallback(project_dir: Path, max_depth: int = 3) -> list[dict]:
    """无 manifest 时扫描项目内 package.json / pom.xml 目录作为构建目标。"""
    out = []
    if (project_dir / "package.json").exists():
        out.append({"starter": "root", "target": ""})
    for rel in sorted(_iter_pkg_dirs(project_dir, max_depth=max_depth)):
        out.append({"starter": rel, "target": rel})
    for rel in sorted(_iter_maven_dirs(project_dir, max_depth=max_depth)):
        out.append({"starter": rel, "target": rel})
    return out


def detect_package_manager(project_dir: Path, prefer: str | None = None) -> str:
    """按 lockfile / workspace 文件探测包管理器，默认 pnpm（starter 生成约定）。"""
    if prefer:
        return prefer
    for lock, pm in (
        ("pnpm-lock.yaml", "pnpm"),
        ("pnpm-workspace.yaml", "pnpm"),
        ("yarn.lock", "yarn"),
        ("package-lock.json", "npm"),
    ):
        if (project_dir / lock).exists():
            return pm
    return "pnpm"


def build_script_for(pkg: dict) -> str | None:
    """从 package.json scripts 中选构建脚本（build 优先，其次 build:h5 等）。"""
    if not isinstance(pkg, dict):
        return None
    scripts = pkg.get("scripts") or {}
    if not isinstance(scripts, dict):
        return None
    for name in BUILD_SCRIPT_PRIORITY:
        if name in scripts:
            return name
    for name in sorted(scripts):
        if name.startswith("build"):
            return name
    return None


def _read_pkg(pkg_path: Path) -> dict:
    try:
        data = json.loads(pkg_path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:  # noqa: BLE001
        return {}


def resolve_targets(project_dir: Path, manifest: dict | None) -> list[dict]:
    """解析构建目标列表（含 workspace 根识别与构建脚本探测）。"""
    specs = manifest_targets(manifest) or scan_fallback(project_dir)
    is_workspace = (project_dir / "pnpm-workspace.yaml").exists()
    targets = []
    for spec in specs:
        rel = str(spec.get("target") or "").strip()
        is_root = rel in ("", ".")
        path = project_dir if is_root else (project_dir / rel).resolve()
        pkg_path = path / "package.json"
        pom_path = path / "pom.xml"
        if pkg_path.exists():
            pkg = _read_pkg(pkg_path)
            build_script = None if (is_root and is_workspace) else build_script_for(pkg)
            targets.append({
                "kind": "node",
                "starter": spec.get("starter") or ("root" if is_root else rel),
                "rel": "." if is_root else rel,
                "path": str(path),
                "is_root": is_root,
                "is_workspace_root": bool(is_root and is_workspace),
                "name": pkg.get("name", ""),
                "build_script": build_script,
            })
        elif pom_path.exists():
            # Maven 目标：install 跳过（package 阶段自带依赖解析），build 用 mvn package
            targets.append({
                "kind": "maven",
                "starter": spec.get("starter") or ("root" if is_root else rel),
                "rel": "." if is_root else rel,
                "path": str(path),
                "is_root": is_root,
                "is_workspace_root": False,
                "name": f"maven:{pom_path.parent.name}",
                "build_script": "mvn package",
                "build_cmd": ["mvn", "-q", "-DskipTests", "package"],
            })
    return targets


def _run_cmd(cmd: list[str], cwd: Path, timeout: float, plan_only: bool) -> dict:
    """执行单条命令；plan 模式下只记录命令不执行。"""
    started = time.time()
    cmd_text = " ".join(cmd)
    if plan_only:
        return {"cmd": cmd_text, "state": "plan", "returncode": None, "elapsed": 0.0, "tail": ""}
    try:
        proc = subprocess.run(
            cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout,
        )
        tail = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()[-OUTPUT_TAIL:]
        return {
            "cmd": cmd_text,
            "state": "ok" if proc.returncode == 0 else "fail",
            "returncode": proc.returncode,
            "elapsed": round(time.time() - started, 1),
            "tail": tail,
        }
    except subprocess.TimeoutExpired:
        return {
            "cmd": cmd_text,
            "state": "fail",
            "returncode": "TIMEOUT",
            "elapsed": round(time.time() - started, 1),
            "tail": f"Timed out after {timeout}s",
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "cmd": cmd_text,
            "state": "fail",
            "returncode": "ERROR",
            "elapsed": round(time.time() - started, 1),
            "tail": str(exc)[:300],
        }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="AI Bootstrap — Starter Build Smoke Checker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 build-smoke.py --dir /path/to/project
  python3 build-smoke.py --dir /path/to/project --skip-install
  python3 build-smoke.py --dir /path/to/project --only frontend,apps/web
  python3 build-smoke.py --dir /path/to/project --plan
  python3 build-smoke.py --dir /path/to/project --json
        """,
    )
    parser.add_argument("--dir", required=True, help="Project directory")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--plan", action="store_true", help="只打印计划，不真正安装/构建")
    parser.add_argument("--skip-install", action="store_true", help="跳过 install，只执行构建（要求依赖已安装）")
    parser.add_argument("--only", default="", help="逗号分隔的相对目录白名单（如 frontend,apps/web）")
    parser.add_argument("--pm", default="", help="覆盖包管理器（pnpm/npm/yarn）")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help=f"单条命令超时秒数（默认 {DEFAULT_TIMEOUT}）")
    parser.add_argument("--install-args", default="", help="传给 install 的额外参数（如 --offline）")
    args = parser.parse_args()

    project_dir = Path(args.dir).resolve()
    if not project_dir.exists():
        print(f"❌ Directory does not exist: {args.dir}", file=sys.stderr)
        return 2

    manifest = load_manifest(project_dir)
    targets = resolve_targets(project_dir, manifest)
    if args.only:
        allowed = {p.strip().strip("./") for p in args.only.split(",") if p.strip()}
        targets = [t for t in targets if t["rel"].strip("./") in allowed]
    if not targets:
        print("  ⚠ No buildable starter targets found (no package.json).")
        return 0 if args.json else 1

    pm = detect_package_manager(project_dir, args.pm or None)
    install_args = shlex.split(args.install_args) if args.install_args else []

    results = []
    failures = 0
    for target in targets:
        cwd = Path(target["path"])
        install = None
        is_maven = target.get("kind") == "maven"
        if not args.skip_install and not is_maven:
            install = _run_cmd([pm, "install", *install_args], cwd, args.timeout, args.plan)
        build = None
        if is_maven:
            build = _run_cmd(target["build_cmd"], cwd, args.timeout, args.plan)
        elif target["build_script"]:
            build = _run_cmd([pm, "run", target["build_script"]], cwd, args.timeout, args.plan)
        else:
            build = {
                "cmd": "(workspace root: 各 app 单独构建)",
                "state": "skip",
                "returncode": None,
                "elapsed": 0.0,
                "tail": "workspace 根目录只负责 install，构建以各 app 为单位",
            }
        for step in (install, build):
            if step and step.get("state") == "fail":
                failures += 1
        results.append({
            "starter": target["starter"],
            "dir": target["rel"],
            "name": target["name"],
            "is_workspace_root": target["is_workspace_root"],
            "build_script": target["build_script"],
            "package_manager": pm,
            "install": install,
            "build": build,
        })

    if args.json:
        print(json.dumps({
            "package_manager": pm,
            "plan": args.plan,
            "targets": results,
            "failures": failures,
        }, indent=2, ensure_ascii=False))
    else:
        has_maven = any(t.get("kind") == "maven" for t in targets)
        pm_label = f"{pm} + maven" if has_maven else pm
        print(f"\n  AI Bootstrap — Starter Build Smoke Checker ({'PLAN' if args.plan else 'REAL'})")
        print(f"  Package manager: {pm_label}   Targets: {len(results)}")
        print(f"  {'Target':<26} {'Install':<10} {'Build':<10} {'Build script':<16} Time(s)")
        print(f"  {'-' * 90}")
        for r in results:
            install_mark = "✅" if r["install"] and r["install"]["state"] == "ok" else (
                "⏭" if (r["install"] is None or r["install"]["state"] == "plan") else "❌"
            )
            build_state = r["build"]["state"] if r["build"] else "—"
            build_mark = {"ok": "✅", "fail": "❌", "skip": "—", "plan": "⏭"}.get(build_state, "?")
            elapsed = (r["install"] or {}).get("elapsed", 0) + (r["build"] or {}).get("elapsed", 0)
            print(f"  {r['dir']:<26} {install_mark:<10} {build_mark:<10} {(r['build_script'] or '—'):<16} {elapsed:.1f}")
            for step in ("install", "build"):
                entry = r.get(step)
                if entry and entry.get("state") == "fail" and entry.get("tail"):
                    print(f"    ↳ {step} failed ({r['dir']}): {entry['tail'][-300:]}")
        print(f"\n  Summary: {len(results)} targets, {failures} failures\n")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
