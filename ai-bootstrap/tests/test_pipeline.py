import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from generate import load_blueprint  # noqa: E402
from wizard import recommend_blueprint, stack_summary, write_stack_decision  # noqa: E402
from yaml_utils import load_yaml_text  # noqa: E402
from framework_gate import DEPRECATED_COMPONENTS, FRAMEWORK_CONSTRAINTS  # noqa: E402


class BootstrapPipelineTests(unittest.TestCase):
    def run_script(self, script: str, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / script), *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_all_blueprints_parse_with_expected_schema(self):
        expected = {
            "next-fullstack": ("next", "postgres"),
            "react-fastapi": ("react", "postgres"),
            "react-springboot": ("react", "postgres"),
            "vue-django": ("vue", "postgres"),
            "go-microservice": ("none", "postgres"),
            "rust-axum-api": ("none", "sqlite"),
            "python-ml-service": ("none", "postgres"),
            "nuxt-ai-fullstack": ("nuxt", "sqlite"),
            "uni-app-nitro": ("uni-app", "sqlite"),
            "vue-springboot": ("vue", "postgres"),
        }
        for blueprint_id, (frontend, database) in expected.items():
            with self.subTest(blueprint=blueprint_id):
                blueprint = load_blueprint(blueprint_id)
                self.assertIsNotNone(blueprint)
                self.assertEqual(blueprint["stack"]["frontend"]["framework"], frontend)
                self.assertEqual(blueprint["stack"]["database"]["primary"], database)
                self.assertIsInstance(blueprint["tags"], list)
                self.assertIn("layout", blueprint)
                self.assertIsInstance(blueprint["layout"]["key_dirs"], dict)
                self.assertIn("commands", blueprint)
                self.assertIn("install", blueprint["commands"])
                self.assertIn("dev", blueprint["commands"])

        ml = load_blueprint("python-ml-service")
        self.assertEqual(ml["stack"]["backend"]["framework"], "fastapi")
        self.assertEqual(ml["stack"]["ml"]["framework"], "pytorch")

        nuxt_ai = load_blueprint("nuxt-ai-fullstack")
        self.assertEqual(nuxt_ai["stack"]["ai"]["sdk"], "vercel-ai-sdk")
        self.assertEqual(nuxt_ai["stack"]["database"]["production"], "turso/libsql")
        self.assertEqual(nuxt_ai["design_system"]["theme_entry"]["global_tokens"], "app/assets/css/main.css")
        self.assertTrue(nuxt_ai.get("skills"))
        self.assertEqual(nuxt_ai["skills"][0]["install"], "npx skills add nuxt/ui")

        spring = load_blueprint("react-springboot")
        self.assertEqual(spring["stack"]["backend"]["framework"], "spring-boot")
        self.assertEqual(spring["design_system"]["ui_library"], "antd")
        self.assertEqual(spring["stack"]["database"]["alternative"], "mysql")

        uni = load_blueprint("uni-app-nitro")
        self.assertEqual(uni["stack"]["backend"]["package"], "nitropack")
        self.assertEqual(uni["design_system"]["ui_library"], "vant + uni-ui")
        self.assertIn("apps/mobile/", uni["layout"]["key_dirs"])

    def test_stack_summary_exposes_the_complete_choice(self):
        summary = stack_summary(load_blueprint("nuxt-ai-fullstack"))
        self.assertIn("nuxt 4.x + nuxt-ui", summary)
        self.assertIn("nitro 2.x / typescript / typed REST + server functions", summary)
        self.assertIn("vercel-ai-sdk", summary)
        self.assertIn("sqlite → turso/libsql", summary)
        self.assertIn("pnpm", summary)

    def test_empty_project_preferences_override_runtime_default(self):
        blueprint, confidence = recommend_blueprint(
            {
                "is_empty": True,
                "environment": {"runtimes": [{"name": "node"}]},
                "project": {"languages": []},
            },
            {"priority": "demo", "unified_language": "yes", "deployment": "vercel"},
        )
        self.assertEqual(blueprint["id"], "nuxt-ai-fullstack")
        self.assertGreater(confidence, 0.9)

    def test_ai_and_enterprise_preferences_rank_default_blueprints(self):
        base_detection = {
            "is_empty": True,
            "environment": {"runtimes": [{"name": "node"}]},
            "project": {"languages": []},
        }
        ai_blueprint, _ = recommend_blueprint(
            base_detection,
            {"priority": "ai", "unified_language": "yes", "deployment": "vercel"},
        )
        self.assertEqual(ai_blueprint["id"], "nuxt-ai-fullstack")

        enterprise_blueprint, _ = recommend_blueprint(
            base_detection,
            {"priority": "enterprise", "unified_language": "no", "deployment": "docker"},
        )
        self.assertEqual(enterprise_blueprint["id"], "react-springboot")

    def test_stack_decision_is_persisted_without_overwriting_existing_file(self):
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-decision-") as project:
            research = Path(project) / "docs" / "00-research"
            research.mkdir(parents=True)
            original = research / "stack-decision.md"
            original.write_text("KEEP THIS DECISION", encoding="utf-8")

            decision_path = write_stack_decision(
                project,
                "nuxt-ai-fullstack",
                preferences={"priority": "demo", "deployment": "vercel"},
            )
            self.assertEqual(original.read_text(encoding="utf-8"), "KEEP THIS DECISION")
            self.assertNotEqual(decision_path, original)
            self.assertTrue(decision_path.exists())
            decision_text = decision_path.read_text(encoding="utf-8")
            self.assertIn("vercel-ai-sdk", decision_text)
            self.assertIn("选型偏好", decision_text)

    def test_fresh_generation_is_complete_and_valid(self):
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-test-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "next-fullstack",
                "--name", "DemoApp", "--agents", "codex,cursor",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((Path(project) / "README.md").exists())
            self.assertTrue((Path(project) / ".gitignore").exists())
            for phase in (
                "00-research", "01-requirements", "02-specs", "03-plans",
                "04-reviews", "05-verification", "06-decisions",
            ):
                self.assertTrue((Path(project) / "docs" / phase / "README.md").exists())
            generated_text = "\n".join(p.read_text(encoding="utf-8") for p in Path(project).rglob("*.md"))
            self.assertNotIn("{{", generated_text)
            self.assertNotIn("{%", generated_text)
            self.assertIn('type: "postgres"', (Path(project) / "docs" / "PROJECT_PROFILE.md").read_text())
            token_spec = Path(project) / "docs" / "00-research" / "design-token-spec.md"
            self.assertTrue(token_spec.exists())
            token_text = token_spec.read_text(encoding="utf-8")
            self.assertIn("shadcn", token_text)
            self.assertIn("## 4. 语义颜色", token_text)
            self.assertIn("UI 库官方范式", token_text)
            self.assertIn("shadcn/ui v3", token_text)
            readme_text = (Path(project) / "README.md").read_text(encoding="utf-8")
            self.assertIn("应用源码目录", readme_text)
            self.assertIn("docs/DESIGN.md", readme_text)  # 目录契约单一来源：README 只引用 DESIGN
            self.assertIn("pnpm install", readme_text)
            self.assertIn("pnpm dev", readme_text)
            self.assertIn("pnpm test", readme_text)
            design_text = (Path(project) / "docs" / "DESIGN.md").read_text(encoding="utf-8")
            self.assertIn("项目目录契约", design_text)
            self.assertIn("apps/web", design_text)
            self.assertIn("apps/api", design_text)
            self.assertTrue((Path(project) / ".ai-bootstrap" / "bootstrap-manifest.yaml").exists())
            for legacy_path in (
                "ADR", "TASKS", "DECISIONS", "REVIEWS", "PROJECT_PROFILE.md",
                "DESIGN.md", "MEMORY.md", "bootstrap-manifest.yaml",
            ):
                self.assertFalse((Path(project) / legacy_path).exists(), legacy_path)

            validation = self.run_script("validate.py", "--dir", project, "--json")
            self.assertEqual(validation.returncode, 0, validation.stderr)
            report = json.loads(validation.stdout)
            self.assertEqual(report["status"], "passed")
            self.assertEqual(report["summary"]["score"], 100)

            profile = load_yaml_text(
                (Path(project) / "docs" / "PROJECT_PROFILE.md").read_text(encoding="utf-8")
            )
            agents = profile["dna"]["governance"]["agents"]
            self.assertEqual([agent["id"] for agent in agents], ["codex", "cursor"])

    def test_every_blueprint_generates_valid_language_aware_governance(self):
        expected_languages = {
            "next-fullstack": "typescript",
            "react-fastapi": "typescript",
            "react-springboot": "typescript",
            "vue-django": "typescript",
            "go-microservice": "go",
            "rust-axum-api": "rust",
            "python-ml-service": "python",
            "nuxt-ai-fullstack": "typescript",
            "uni-app-nitro": "typescript",
        }
        for blueprint_id, language in expected_languages.items():
            with self.subTest(blueprint=blueprint_id):
                with tempfile.TemporaryDirectory(prefix="ai-bootstrap-blueprint-") as project:
                    result = self.run_script(
                        "generate.py", "--dir", project, "--blueprint", blueprint_id,
                        "--agents", "codex,cursor",
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    validation = self.run_script("validate.py", "--dir", project, "--json")
                    self.assertEqual(validation.returncode, 0, validation.stderr)
                    self.assertEqual(json.loads(validation.stdout)["status"], "passed")

                    profile_text = (Path(project) / "docs" / "PROJECT_PROFILE.md").read_text(
                        encoding="utf-8"
                    )
                    profile = load_yaml_text(profile_text)
                    self.assertEqual(profile["dna"]["tech_stack"]["primary_language"], language)
                    self.assertEqual(
                        [agent["id"] for agent in profile["dna"]["governance"]["agents"]],
                        ["codex", "cursor"],
                    )
                    if language in {"go", "rust", "python"}:
                        self.assertNotIn("Server Components", profile_text)

    def test_nuxt_blueprint_generates_multi_app_starter(self):
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-nuxt-starter-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "nuxt-ai-fullstack",
                "--name", "MatchCV", "--agents", "codex,cursor",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            for expected in (
                "pnpm-workspace.yaml",
                "turbo.json",
                "tsconfig.base.json",
                "apps/app-web-hr/app/composables/useAuth.ts",
                "apps/app-web-hr/app/composables/useJobs.ts",
                "apps/app-web-hr/app/middleware/author-auth.ts",
                "apps/app-web-hr/app/pages/login.vue",
                "apps/app-web-hr/app/pages/jobs/new.vue",
                "apps/app-web-hr/app/pages/jobs/[id]/edit.vue",
                "apps/app-web-hr/app/utils/seed.ts",
                "apps/app-web-hr/app/components/EmptyState.vue",
                "apps/app-web-platform/app/layouts/default.vue",
                "apps/app-web-platform/app/components/AppSidebarHeader.vue",
                "apps/app-web-platform/app/components/UserMenu.vue",
                "apps/app-web-platform/app/components/NotificationsSlideover.vue",
                "apps/app-web-platform/app/composables/useDashboard.ts",
                "apps/app-web-platform/app/composables/useAuth.ts",
                "apps/app-web-platform/app/middleware/admin-auth.ts",
                "apps/app-web-platform/app/pages/login.vue",
                "apps/app-web-platform/app/utils/dashboard.ts",
                "apps/app-web-server/routes/health.ts",
                "apps/app-web-server/routes/api/echo.ts",
            ):
                self.assertTrue((Path(project) / expected).exists(), expected)

            # {{VARIABLE}} rendering across copied templates
            root_pkg = (Path(project) / "package.json").read_text(encoding="utf-8")
            self.assertIn('"name": "matchcv"', root_pkg)
            self.assertNotIn("{{", root_pkg)
            hr_pkg = (Path(project) / "apps" / "app-web-hr" / "package.json").read_text(encoding="utf-8")
            self.assertIn('"name": "@matchcv/web-hr"', hr_pkg)
            app_logo = (
                Path(project) / "apps" / "app-web-hr" / "app" / "components" / "AppLogo.vue"
            ).read_text(encoding="utf-8")
            self.assertIn("MatchCV", app_logo)

            # Nuxt UI v4 官方主题范式（@theme static + ui.colors + tailwindcss + error.vue）
            hr_css = (Path(project) / "apps/app-web-hr/app/assets/css/main.css").read_text(encoding="utf-8")
            for needle in ('@import "tailwindcss"', '@import "@nuxt/ui"', "@theme static", "--color-brand-600"):
                self.assertIn(needle, hr_css)
            self.assertNotIn("--mc-", hr_css)
            hr_app_config = (Path(project) / "apps/app-web-hr/app/app.config.ts").read_text(encoding="utf-8")
            self.assertIn("primary: 'brand'", hr_app_config)
            self.assertIn("accent: 'accent'", hr_app_config)
            self.assertIn("neutral: 'slate'", hr_app_config)
            self.assertIn("tailwindcss", hr_pkg)
            hr_nuxt_config = (Path(project) / "apps/app-web-hr/nuxt.config.ts").read_text(encoding="utf-8")
            self.assertIn("ui:", hr_nuxt_config)
            self.assertIn("theme:", hr_nuxt_config)
            for app in ("app-web-hr", "app-web-platform"):
                self.assertTrue((Path(project) / f"apps/{app}/app/error.vue").exists())
                app_css = (Path(project) / f"apps/{app}/app/assets/css/main.css").read_text(encoding="utf-8")
                self.assertNotIn("--mc-", app_css)

            manifest = (Path(project) / ".ai-bootstrap" / "bootstrap-manifest.yaml").read_text(
                encoding="utf-8"
            )
            self.assertIn("multi-app-monorepo", manifest)
            self.assertIn("app-web-hr", manifest)
            for doc in ("AGENTS.md", "README.md", "docs/PROJECT_PROFILE.md"):
                doc_text = (Path(project) / doc).read_text(encoding="utf-8")
                self.assertIn("npx skills add nuxt/ui", doc_text)
                self.assertIn("/nuxt-ui", doc_text)

            validation = self.run_script("validate.py", "--dir", project, "--json")
            self.assertEqual(validation.returncode, 0, validation.stderr)
            report = json.loads(validation.stdout)
            self.assertEqual(report["status"], "passed")

        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-nuxt-no-starter-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "nuxt-ai-fullstack",
                "--no-starter", "--agents", "codex,cursor",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(
                (Path(project) / "apps" / "app-web-hr" / "app" / "composables" / "useAuth.ts").exists()
            )




    def test_ui_stack_conformance_rejects_legacy_theme(self):
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-conformance-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "nuxt-ai-fullstack",
                "--name", "MatchCV", "--agents", "codex,cursor",
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            # 官方范式生成品必须通过 ui-stack-conformance
            validation = self.run_script("validate.py", "--dir", project, "--json")
            self.assertEqual(validation.returncode, 0, validation.stderr)
            report = json.loads(validation.stdout)
            conformance = next(c for c in report["checks"] if c["name"] == "ui-stack-conformance")
            self.assertEqual(conformance["status"], "passed")

            # 回退成遗留 --mc-* 老范式（无 tailwindcss、无 @theme）后必须被拦截
            hr_main_css = Path(project) / "apps/app-web-hr/app/assets/css/main.css"
            legacy_css = """@import '@fontsource-variable/inter';

:root {
  --mc-canvas: #f6f8fc;
  --mc-surface: #ffffff;
  --mc-primary: #4f46e5;
}

body {
  background-color: var(--mc-canvas);
  color: var(--mc-ink);
}
"""
            hr_main_css.write_text(legacy_css, encoding="utf-8")

            hr_pkg_path = Path(project) / "apps/app-web-hr/package.json"
            pkg = json.loads(hr_pkg_path.read_text(encoding="utf-8"))
            pkg.get("dependencies", {}).pop("tailwindcss", None)
            pkg.get("devDependencies", {}).pop("tailwindcss", None)
            hr_pkg_path.write_text(json.dumps(pkg, indent=2), encoding="utf-8")

            legacy = self.run_script("validate.py", "--dir", project, "--json")
            self.assertEqual(legacy.returncode, 1, legacy.stderr)  # 校验门禁：存在失败项时 validate.py 退出码为 1
            legacy_report = json.loads(legacy.stdout)
            legacy_check = next(c for c in legacy_report["checks"] if c["name"] == "ui-stack-conformance")
            self.assertEqual(legacy_check["status"], "failed")
            errors_text = "\n".join(legacy_check["errors"])
            self.assertIn("tailwindcss", errors_text)
            self.assertIn('@import "tailwindcss"', errors_text)
            self.assertTrue(any("--mc-" in w for w in legacy_check["warnings"]))

    def test_existing_files_are_protected_until_force(self):
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-protect-") as project:
            agents = Path(project) / "AGENTS.md"
            agents.write_text("KEEP THIS FILE", encoding="utf-8")
            result = self.run_script("generate.py", "--dir", project, "--blueprint", "next-fullstack")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(agents.read_text(encoding="utf-8"), "KEEP THIS FILE")

            forced = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "next-fullstack", "--force",
            )
            self.assertEqual(forced.returncode, 0, forced.stderr)
            self.assertNotEqual(agents.read_text(encoding="utf-8"), "KEEP THIS FILE")

    def test_deep_detection_handles_python_only_project(self):
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-detect-") as project:
            (Path(project) / "pyproject.toml").write_text("", encoding="utf-8")
            result = self.run_script("detect.py", "--dir", project, "--deep", "--json")
            self.assertIn(result.returncode, (0, 1))
            payload = json.loads(result.stdout)
            self.assertEqual(payload["project"]["languages"][0]["name"], "python")

    def test_detection_handles_deno_project(self):
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-deno-") as project:
            (Path(project) / "deno.json").write_text('{"imports": {}}', encoding="utf-8")
            result = self.run_script("detect.py", "--dir", project, "--json")
            self.assertIn(result.returncode, (0, 1), result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["project"]["languages"][0]["runtime"], "deno")

    def test_validation_rejects_missing_agent_definitions(self):
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-agent-validation-") as project:
            generated = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "next-fullstack",
            )
            self.assertEqual(generated.returncode, 0, generated.stderr)
            (Path(project) / "AGENTS.md").write_text(
                "permissions: present\n@agent\ncontext_router: standard\n",
                encoding="utf-8",
            )
            validation = self.run_script("validate.py", "--dir", project, "--json")
            report = json.loads(validation.stdout)
            agent_check = next(item for item in report["checks"] if item["name"] == "agent-context")
            self.assertEqual(agent_check["status"], "warning")
            self.assertIn("No agent definitions found", agent_check["warnings"])

    def test_auto_resolves_detected_next_project(self):
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-auto-") as project:
            (Path(project) / "package.json").write_text(
                '{"dependencies":{"next":"15.0.0","typescript":"5.0.0"}}',
                encoding="utf-8",
            )
            result = self.run_script("generate.py", "--dir", project, "--blueprint", "auto")
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = (Path(project) / ".ai-bootstrap" / "bootstrap-manifest.yaml").read_text(encoding="utf-8")
            self.assertIn('id: "next-fullstack"', manifest)

    def test_framework_gate_registry_is_consistent(self):
        """框架门禁注册表：每个废弃组件都有替代名，且约束说明包含替代名。"""
        self.assertTrue(DEPRECATED_COMPONENTS)
        for deprecated, replacement in DEPRECATED_COMPONENTS.items():
            self.assertNotEqual(deprecated, replacement)
            self.assertTrue(deprecated.startswith("U"), deprecated)
        all_notes = "\n".join(
            note for item in FRAMEWORK_CONSTRAINTS for note in item.get("notes", [])
        )
        for replacement in DEPRECATED_COMPONENTS.values():
            self.assertIn(replacement, all_notes, f"约束说明缺少替代名 {replacement}")
        # UI 栈官方范式约束必须齐全（nuxt-ui / vant / element-plus / antd / shadcn / naive-ui）
        registered = {item.get("library") for item in FRAMEWORK_CONSTRAINTS}
        for library in ("@nuxt/ui", "vant", "element-plus", "antd", "shadcn/ui", "naive-ui"):
            self.assertIn(library, registered, f"FRAMEWORK_CONSTRAINTS 缺少 {library} 约束")

    def test_nuxt_starter_renders_framework_constraints_and_passes_gate(self):
        """Nuxt 生成项目：DESIGN.md 记录 UFormField 约束；源码不含 UFormGroup；gate 校验通过。"""
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-nuxt-gate-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "nuxt-ai-fullstack",
                "--name", "MatchCV", "--agents", "codex,cursor",
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            design = (Path(project) / "docs" / "DESIGN.md").read_text(encoding="utf-8")
            self.assertIn("框架约束", design)
            self.assertIn("UFormField", design)
            self.assertIn("UFormGroup", design)  # 约束说明里应点名废弃组件
            self.assertIn("framework-component-gate", design)

            # 生成源码不得出现已废弃组件
            for f in Path(project).rglob("*"):
                if f.suffix not in {".vue", ".ts", ".tsx", ".js", ".jsx", ".mjs"}:
                    continue
                if any(part in {".nuxt", "node_modules", ".output", "dist"} for part in f.parts):
                    continue
                self.assertNotIn("UFormGroup", f.read_text(encoding="utf-8", errors="replace"), f)

            validation = self.run_script("validate.py", "--dir", project, "--json")
            self.assertEqual(validation.returncode, 0, validation.stderr)
            report = json.loads(validation.stdout)
            self.assertEqual(report["status"], "passed")
            gate = next(item for item in report["checks"] if item["name"] == "framework-component-gate")
            self.assertEqual(gate["status"], "passed", gate["details"])
            self.assertGreater(gate["details"]["files_scanned"], 0)

    def test_validate_rejects_deprecated_ui_components(self):
        """负向测试：注入 UFormGroup 后 validate 必须失败并给出替代建议。"""
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-nuxt-gate-fail-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "nuxt-ai-fullstack",
                "--name", "MatchCV", "--agents", "codex,cursor",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            login = Path(project) / "apps" / "app-web-hr" / "app" / "pages" / "login.vue"
            self.assertTrue(login.exists())
            login.write_text(
                login.read_text(encoding="utf-8")
                + "\n<UFormGroup label=\"违规\"></UFormGroup>\n",
                encoding="utf-8",
            )
            validation = self.run_script("validate.py", "--dir", project, "--json")
            report = json.loads(validation.stdout)
            self.assertEqual(report["status"], "failed")
            gate = next(item for item in report["checks"] if item["name"] == "framework-component-gate")
            self.assertEqual(gate["status"], "failed")
            self.assertTrue(any("UFormGroup" in err and "UFormField" in err for err in gate["errors"]))



    def test_uni_app_blueprint_generates_vant_mobile_starter(self):
        """uni-app-nitro 生成：Vant 4 官方范式 + --van-* 令牌 + mock-first 页面，validate 全 passed。"""
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-vant-starter-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "uni-app-nitro",
                "--name", "UniDemo", "--agents", "codex,cursor",
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            # 多应用 starter：根 + apps/mobile（含 {{VARIABLE}} 渲染）
            root_pkg = (Path(project) / "package.json").read_text(encoding="utf-8")
            self.assertIn('"name": "unidemo"', root_pkg)
            self.assertNotIn("{{", root_pkg)
            mobile = Path(project) / "apps" / "mobile"
            self.assertTrue((mobile / "package.json").exists())
            self.assertTrue((mobile / "src" / "main.ts").exists())

            # Vant 4 官方范式：全量 css + app.use() 注册 + 无 babel-plugin-import
            pkg = (mobile / "package.json").read_text(encoding="utf-8")
            self.assertIn('"vant"', pkg)
            self.assertNotIn("babel-plugin-import", pkg)
            main_ts = (mobile / "src" / "main.ts").read_text(encoding="utf-8")
            self.assertIn("vant/lib/index.css", main_ts)
            self.assertIn("app.use(Button)", main_ts)
            self.assertNotIn("VantResolver", main_ts)

            # 设计令牌：--van-* 全局覆盖 + uni.scss SCSS 令牌
            app_vue = (mobile / "src" / "App.vue").read_text(encoding="utf-8")
            self.assertIn("--van-primary-color", app_vue)
            uni_scss = (mobile / "src" / "uni.scss").read_text(encoding="utf-8")
            self.assertIn("$primary: #4f46e5", uni_scss)

            # 组件基线 + 函数式 API
            pages_text = "\n".join(
                f.read_text(encoding="utf-8") for f in (mobile / "src" / "pages").rglob("*.vue")
            )
            self.assertIn("<van-button", pages_text)
            self.assertIn("van-config-provider", pages_text)
            self.assertIn("showToast", pages_text)
            self.assertIn("showDialog", pages_text)

            validation = self.run_script("validate.py", "--dir", project, "--json")
            self.assertEqual(validation.returncode, 0, validation.stderr)
            report = json.loads(validation.stdout)
            self.assertEqual(report["status"], "passed")
            vant_check = next(
                c for c in report["checks"]
                if c["name"] == "ui-stack-conformance" and c["status"] != "skipped"
            )
            self.assertEqual(vant_check["status"], "passed", vant_check.get("warnings"))

    def test_vant_conformance_rejects_mixed_import_anti_pattern(self):
        """负向测试：全量 css 与 VantResolver 按需引入混用必须被 ui-stack-conformance 拦截。"""
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-vant-fail-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "uni-app-nitro",
                "--name", "UniDemo", "--agents", "codex,cursor",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            mobile = Path(project) / "apps" / "mobile"
            main_ts = mobile / "src" / "main.ts"
            main_ts.write_text(
                main_ts.read_text(encoding="utf-8")
                + "\nimport { VantResolver } from '@vant/auto-import-resolver'\n",
                encoding="utf-8",
            )
            vite_cfg = mobile / "vite.config.ts"
            vite_cfg.write_text(
                vite_cfg.read_text(encoding="utf-8").replace(
                    "plugins: [uni()],",
                    "plugins: [uni(), Components({ resolvers: [VantResolver()] })],",
                ),
                encoding="utf-8",
            )
            pkg_path = mobile / "package.json"
            pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
            pkg["devDependencies"]["@vant/auto-import-resolver"] = "^1.10.0"
            pkg["devDependencies"]["unplugin-vue-components"] = "^28.0.0"
            pkg_path.write_text(json.dumps(pkg, indent=2), encoding="utf-8")

            validation = self.run_script("validate.py", "--dir", project, "--json")
            report = json.loads(validation.stdout)
            self.assertEqual(report["status"], "failed")
            vant_check = next(
                c for c in report["checks"]
                if c["name"] == "ui-stack-conformance" and c["status"] != "skipped"
            )
            self.assertEqual(vant_check["status"], "failed")
            errors_text = "\n".join(vant_check["errors"])
            self.assertIn("混用", errors_text)



    # ── Element Plus / Ant Design 官方范式（P0）────────────────────────────────

    def test_vue_element_plus_blueprint_generates_ep_starter(self):
        """vue-element-plus-nitro 生成：Element Plus 2.x 官方范式 + --el-* 令牌 + mock-first 页面，validate 全 passed。"""
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-ep-starter-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "vue-element-plus-nitro",
                "--name", "EPDemo", "--agents", "codex,cursor",
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            root_pkg = (Path(project) / "package.json").read_text(encoding="utf-8")
            self.assertIn('"name": "epdemo"', root_pkg)
            self.assertNotIn("{{", root_pkg)
            web = Path(project) / "apps" / "web"
            self.assertTrue((web / "package.json").exists())
            self.assertTrue((web / "src" / "main.ts").exists())
            self.assertTrue((web / "src" / "styles" / "tokens.css").exists())
            self.assertTrue((Path(project) / "apps" / "api" / "package.json").exists())

            # Element Plus 2.x 官方完整引入范式
            pkg = (web / "package.json").read_text(encoding="utf-8")
            self.assertIn('"element-plus"', pkg)
            self.assertNotIn("babel-plugin-import", pkg)
            main_ts = (web / "src" / "main.ts").read_text(encoding="utf-8")
            self.assertIn("element-plus/dist/index.css", main_ts)
            self.assertIn("app.use(ElementPlus)", main_ts)
            self.assertNotIn("VantResolver", main_ts)

            # 设计令牌：--el-* 全局覆盖 + 官方 ConfigProvider locale + Volar 类型
            tokens = (web / "src" / "styles" / "tokens.css").read_text(encoding="utf-8")
            self.assertIn("--el-color-primary", tokens)
            app_vue = (web / "src" / "App.vue").read_text(encoding="utf-8")
            self.assertIn("el-config-provider", app_vue)
            self.assertIn("zhCn", app_vue)
            tsconfig = (web / "tsconfig.json").read_text(encoding="utf-8")
            self.assertIn("element-plus/global", tsconfig)

            # 组件基线
            views_text = "\n".join(
                f.read_text(encoding="utf-8") for f in (web / "src" / "views").rglob("*.vue")
            )
            self.assertIn("<el-table", views_text)
            self.assertIn("<el-button", views_text)
            self.assertIn("<el-dialog", views_text)

            validation = self.run_script("validate.py", "--dir", project, "--json")
            self.assertEqual(validation.returncode, 0, validation.stderr)
            report = json.loads(validation.stdout)
            self.assertEqual(report["status"], "passed")
            ep_check = next(
                c for c in report["checks"]
                if c["name"] == "ui-stack-conformance" and c["status"] != "skipped"
            )
            self.assertEqual(ep_check["status"], "passed", ep_check.get("warnings"))

    def test_element_plus_conformance_rejects_mixed_import_anti_pattern(self):
        """负向测试：全量 css 与 ElementPlusResolver 按需引入混用必须被 ui-stack-conformance 拦截。"""
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-ep-fail-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "vue-element-plus-nitro",
                "--name", "EPDemo", "--agents", "codex,cursor",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            web = Path(project) / "apps" / "web"
            vite_cfg = web / "vite.config.ts"
            vite_cfg.write_text(
                vite_cfg.read_text(encoding="utf-8").replace(
                    "plugins: [vue()],",
                    "plugins: [vue(), Components({ resolvers: [ElementPlusResolver()] })],",
                ),
                encoding="utf-8",
            )
            pkg_path = web / "package.json"
            pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
            pkg["devDependencies"]["unplugin-vue-components"] = "^28.0.0"
            pkg["devDependencies"]["unplugin-auto-import"] = "^19.0.0"
            pkg_path.write_text(json.dumps(pkg, indent=2), encoding="utf-8")

            validation = self.run_script("validate.py", "--dir", project, "--json")
            report = json.loads(validation.stdout)
            self.assertEqual(report["status"], "failed")
            ep_check = next(
                c for c in report["checks"]
                if c["name"] == "ui-stack-conformance" and c["status"] != "skipped"
            )
            self.assertEqual(ep_check["status"], "failed")
            errors_text = "\n".join(ep_check["errors"])
            self.assertIn("混用", errors_text)

    def test_react_springboot_blueprint_generates_antd_starter(self):
        """react-springboot 生成：Ant Design v6 官方范式（ConfigProvider theme.token + zhCN + dayjs，无 v5-patch），validate 全 passed。"""
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-antd-starter-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "react-springboot",
                "--name", "AntDemo", "--agents", "codex,cursor",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            frontend = Path(project) / "frontend"
            self.assertTrue((frontend / "package.json").exists())
            self.assertTrue((frontend / "src" / "main.tsx").exists())
            self.assertTrue((frontend / "src" / "theme.ts").exists())
            self.assertIn(
                '"name": "antdemo-frontend"',
                (frontend / "package.json").read_text(encoding="utf-8"),
            )

            pkg = (frontend / "package.json").read_text(encoding="utf-8")
            self.assertIn('"antd"', pkg)
            self.assertIn("@ant-design/icons", pkg)
            self.assertNotIn("@ant-design/v5-patch-for-react-19", pkg)

            main_tsx = (frontend / "src" / "main.tsx").read_text(encoding="utf-8")
            self.assertIn("ConfigProvider", main_tsx)
            self.assertIn("locale={zhCN}", main_tsx)
            self.assertIn("dayjs.locale", main_tsx)
            theme_ts = (frontend / "src" / "theme.ts").read_text(encoding="utf-8")
            self.assertIn("colorPrimary", theme_ts)
            self.assertIn("algorithm", theme_ts)

            app_tsx = (frontend / "src" / "App.tsx").read_text(encoding="utf-8")
            self.assertIn("items={menuItems}", app_tsx)
            self.assertIn("{'AntDemo'}", app_tsx)  # {{PROJECT_NAME}} 占位符已渲染
            self.assertNotIn("{{PROJECT", app_tsx)
            jobs_tsx = (frontend / "src" / "views" / "Jobs.tsx").read_text(encoding="utf-8")
            self.assertIn("<Table", jobs_tsx)
            self.assertIn("<Card", jobs_tsx)
            self.assertIn('variant="outlined"', jobs_tsx)  # v6 写法（取代 v5 bordered）

            validation = self.run_script("validate.py", "--dir", project, "--json")
            self.assertEqual(validation.returncode, 0, validation.stderr)
            report = json.loads(validation.stdout)
            self.assertEqual(report["status"], "passed")
            antd_check = next(
                c for c in report["checks"]
                if c["name"] == "ui-stack-conformance" and c["status"] != "skipped"
            )
            self.assertEqual(antd_check["status"], "passed", antd_check.get("warnings"))

    def test_antd_conformance_rejects_v5_patch_and_deprecated_api(self):
        """负向测试：注入 v5-patch-for-react-19 与 v5 弃用属性必须被 ui-stack-conformance 拦截。"""
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-antd-fail-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "react-springboot",
                "--name", "AntDemo", "--agents", "codex,cursor",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            frontend = Path(project) / "frontend"
            pkg_path = frontend / "package.json"
            pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
            pkg["dependencies"]["@ant-design/v5-patch-for-react-19"] = "^1.0.3"
            pkg_path.write_text(json.dumps(pkg, indent=2), encoding="utf-8")
            login = frontend / "src" / "views" / "Login.tsx"
            login.write_text(
                login.read_text(encoding="utf-8")
                + "\n      <Input bordered placeholder=\"v5 写法\" />\n",
                encoding="utf-8",
            )

            validation = self.run_script("validate.py", "--dir", project, "--json")
            report = json.loads(validation.stdout)
            self.assertEqual(report["status"], "failed")
            antd_check = next(
                c for c in report["checks"]
                if c["name"] == "ui-stack-conformance" and c["status"] != "skipped"
            )
            self.assertEqual(antd_check["status"], "failed")
            errors_text = "\n".join(antd_check["errors"])
            self.assertIn("v5-patch-for-react-19", errors_text)
            self.assertIn("bordered", errors_text)


    # ── shadcn/ui 与 Naive UI 官方范式（P0，范式声明 + conformance 门禁）────────────

    def test_shadcn_blueprints_declare_official_paradigm(self):
        """next-fullstack / react-fastapi（shadcn）必须声明官方安装范式（components.json + Tailwind v4 CSS 变量）。"""
        for blueprint_id in ("next-fullstack", "react-fastapi"):
            with self.subTest(blueprint=blueprint_id):
                blueprint = load_blueprint(blueprint_id)
                paradigm = blueprint["design_system"].get("official_paradigm", "")
                self.assertTrue(paradigm, f"{blueprint_id} 缺少 official_paradigm")
                self.assertIn("shadcn", paradigm.lower())
                self.assertIn("components.json", paradigm)
                self.assertIn("tailwindcss", paradigm.lower())
                self.assertIn("theme_entry", blueprint["design_system"])

    def test_naive_ui_blueprint_declares_official_paradigm(self):
        """vue-django（naive-ui）必须声明官方范式（无 CSS 导入 + n-config-provider theme-overrides + zhCN locale）。"""
        blueprint = load_blueprint("vue-django")
        paradigm = blueprint["design_system"].get("official_paradigm", "")
        self.assertTrue(paradigm, "vue-django 缺少 official_paradigm")
        self.assertIn("naive-ui", paradigm.lower())
        self.assertIn("theme-overrides", paradigm)
        self.assertIn("zhCN", paradigm)

    def test_shadcn_conformance_passes_on_official_layout(self):
        """shadcn 正样例：components.json + @import tailwindcss + --primary/--radius + 语义类名，conformance 必须 passed。"""
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-shadcn-ok-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "react-fastapi",
                "--name", "ShadDemo", "--agents", "codex",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            frontend = Path(project) / "frontend"
            (frontend / "src" / "components" / "ui").mkdir(parents=True, exist_ok=True)
            (frontend / "src" / "lib").mkdir(parents=True, exist_ok=True)
            (frontend / "components.json").write_text(
                '{"style": "new-york", "tailwind": {"css": "src/index.css"}}', encoding="utf-8"
            )
            (frontend / "src" / "index.css").write_text(
                '@import "tailwindcss";\n:root { --primary: #4f46e5; --radius: 0.5rem; }\n',
                encoding="utf-8",
            )
            (frontend / "src" / "components" / "ui" / "button.tsx").write_text(
                "export function Button(){return <button className='bg-primary'>btn</button>}\n",
                encoding="utf-8",
            )
            (frontend / "src" / "lib" / "utils.ts").write_text(
                "export const cn = (...a: string[]) => a.join(' ');\n", encoding="utf-8"
            )
            (frontend / "src" / "App.tsx").write_text(
                "export default function App(){return <div className='bg-primary text-muted'>demo</div>}\n",
                encoding="utf-8",
            )

            validation = self.run_script("validate.py", "--dir", project, "--json")
            self.assertEqual(validation.returncode, 0, validation.stderr)
            report = json.loads(validation.stdout)
            shadcn_check = next(
                c for c in report["checks"]
                if c["name"] == "ui-stack-conformance" and c["status"] != "skipped"
                and "shadcn" in str(c["details"].get("official_pattern", ""))
            )
            self.assertEqual(shadcn_check["status"], "passed", shadcn_check.get("warnings"))
            self.assertEqual(shadcn_check["details"]["shadcn_apps"], 1)

    def test_shadcn_conformance_rejects_babel_plugin_import(self):
        """shadcn 负样例：依赖 babel-plugin-import 必须被 ui-stack-conformance 拦截。"""
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-shadcn-fail-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "react-fastapi",
                "--name", "ShadDemo", "--agents", "codex",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            frontend = Path(project) / "frontend"
            (frontend / "src" / "components" / "ui").mkdir(parents=True, exist_ok=True)
            (frontend / "package.json").write_text(
                '{"dependencies": {"babel-plugin-import": "^1.13.8", "react": "^19.0.0"}}',
                encoding="utf-8",
            )
            (frontend / "components.json").write_text('{}', encoding="utf-8")
            (frontend / "src" / "index.css").write_text(
                '@import "tailwindcss";\n:root { --primary: #4f46e5; --radius: 0.5rem; }\n',
                encoding="utf-8",
            )
            (frontend / "src" / "App.tsx").write_text(
                "export default function App(){return <div className='bg-primary'>demo</div>}\n",
                encoding="utf-8",
            )

            validation = self.run_script("validate.py", "--dir", project, "--json")
            report = json.loads(validation.stdout)
            shadcn_check = next(
                c for c in report["checks"]
                if c["name"] == "ui-stack-conformance" and c["status"] != "skipped"
                and "shadcn" in str(c["details"].get("official_pattern", ""))
            )
            self.assertEqual(shadcn_check["status"], "failed")
            self.assertIn("babel-plugin-import", "\n".join(shadcn_check["errors"]))

    def test_naive_ui_conformance_passes_on_official_layout(self):
        """Naive UI 正样例：无 CSS 导入 + n-config-provider theme-overrides + zhCN/dateZhCN，conformance 必须 passed。"""
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-naive-ok-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "vue-django",
                "--name", "NaiveDemo", "--agents", "codex",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            frontend = Path(project) / "frontend"
            (frontend / "src").mkdir(parents=True, exist_ok=True)
            (frontend / "package.json").write_text(
                '{"dependencies": {"naive-ui": "^2.42.0", "vue": "^3.5.0"}}', encoding="utf-8"
            )
            (frontend / "src" / "theme.ts").write_text(
                "import type { GlobalThemeOverrides } from 'naive-ui'\n"
                "export const themeOverrides: GlobalThemeOverrides = { common: { primaryColor: '#4f46e5' } }\n",
                encoding="utf-8",
            )
            (frontend / "src" / "main.ts").write_text(
                "import { createApp } from 'vue'\nimport App from './App.vue'\ncreateApp(App).mount('#app')\n",
                encoding="utf-8",
            )
            (frontend / "src" / "App.vue").write_text(
                "<template><n-config-provider :theme-overrides=\"themeOverrides\" :locale=\"zhCN\""
                " :date-locale=\"dateZhCN\"><n-button>btn</n-button></n-config-provider></template>\n"
                "<script setup lang='ts'>import { zhCN, dateZhCN } from 'naive-ui'\n"
                "import { themeOverrides } from './theme'\n</script>\n",
                encoding="utf-8",
            )

            validation = self.run_script("validate.py", "--dir", project, "--json")
            self.assertEqual(validation.returncode, 0, validation.stderr)
            report = json.loads(validation.stdout)
            naive_check = next(
                c for c in report["checks"]
                if c["name"] == "ui-stack-conformance" and c["status"] != "skipped"
                and "naive" in str(c["details"].get("official_pattern", "")).lower()
            )
            self.assertEqual(naive_check["status"], "passed", naive_check.get("warnings"))
            self.assertEqual(naive_check["details"]["naive_apps"], 1)

    def test_naive_ui_conformance_rejects_css_import(self):
        """Naive UI 负样例：导入全量 CSS（naive-ui/dist/index.css）必须被 ui-stack-conformance 拦截。"""
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-naive-fail-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "vue-django",
                "--name", "NaiveDemo", "--agents", "codex",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            frontend = Path(project) / "frontend"
            (frontend / "src").mkdir(parents=True, exist_ok=True)
            (frontend / "package.json").write_text(
                '{"dependencies": {"naive-ui": "^2.42.0", "vue": "^3.5.0"}}', encoding="utf-8"
            )
            (frontend / "src" / "main.ts").write_text(
                "import 'naive-ui/dist/index.css'\nimport { createApp } from 'vue'\n",
                encoding="utf-8",
            )
            (frontend / "src" / "App.vue").write_text(
                "<template><n-config-provider :theme-overrides=\"themeOverrides\">"
                "<n-button>btn</n-button></n-config-provider></template>\n",
                encoding="utf-8",
            )

            validation = self.run_script("validate.py", "--dir", project, "--json")
            report = json.loads(validation.stdout)
            naive_check = next(
                c for c in report["checks"]
                if c["name"] == "ui-stack-conformance" and c["status"] != "skipped"
                and "naive" in str(c["details"].get("official_pattern", "")).lower()
            )
            self.assertEqual(naive_check["status"], "failed")
            self.assertIn("naive-ui/dist", "\n".join(naive_check["errors"]))

    # ── shadcn / Naive UI 瘦 DEMO starter（P0，生成即能跑 + 校验即通过）────────────

    def test_react_fastapi_blueprint_generates_shadcn_starter(self):
        """react-fastapi 生成：shadcn/ui v3 官方范式（Tailwind v4 CSS 变量 + 源码拷贝组件 + 语义类名 + @/* 别名），validate 全 passed。"""
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-shadcn-starter-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "react-fastapi",
                "--name", "ShadDemo", "--agents", "codex",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            frontend = Path(project) / "frontend"
            self.assertTrue((frontend / "components.json").exists())
            self.assertTrue((frontend / "src" / "lib" / "utils.ts").exists())
            self.assertTrue((frontend / "src" / "components" / "ui" / "button.tsx").exists())
            self.assertTrue((frontend / "src" / "index.css").exists())

            # shadcn 官方依赖：@tailwindcss/vite + tailwindcss v4 + cva/clsx/tailwind-merge/lucide
            pkg = (frontend / "package.json").read_text(encoding="utf-8")
            self.assertIn("@tailwindcss/vite", pkg)
            self.assertIn('"tailwindcss"', pkg)
            self.assertIn("class-variance-authority", pkg)
            self.assertIn("lucide-react", pkg)
            self.assertNotIn("babel-plugin-import", pkg)

            # 全局 CSS：@import "tailwindcss" + --primary / --radius 主题变量
            css = (frontend / "src" / "index.css").read_text(encoding="utf-8")
            self.assertIn('@import "tailwindcss"', css)
            self.assertIn("--primary", css)
            self.assertIn("--radius", css)

            # 语义类名 + {{PROJECT_NAME}} 渲染
            app_tsx = (frontend / "src" / "App.tsx").read_text(encoding="utf-8")
            self.assertIn("bg-primary", app_tsx)
            self.assertIn("ShadDemo", app_tsx)
            self.assertNotIn("{{PROJECT", app_tsx)
            utils_ts = (frontend / "src" / "lib" / "utils.ts").read_text(encoding="utf-8")
            self.assertIn("twMerge", utils_ts)

            # @/* 路径别名（shadcn add 产物依赖 @/lib/utils）
            vite_cfg = (frontend / "vite.config.ts").read_text(encoding="utf-8")
            self.assertIn("@tailwindcss/vite", vite_cfg)
            tsconfig = (frontend / "tsconfig.json").read_text(encoding="utf-8")
            self.assertIn('"@/*"', tsconfig)

            # 组件基线：源码拷贝进 src/components/ui/
            ui_text = "\n".join(
                f.read_text(encoding="utf-8") for f in (frontend / "src" / "components" / "ui").rglob("*.tsx")
            )
            self.assertIn("Dialog", ui_text)
            self.assertIn("Table", ui_text)
            self.assertIn("Badge", ui_text)

            validation = self.run_script("validate.py", "--dir", project, "--json")
            self.assertEqual(validation.returncode, 0, validation.stderr)
            report = json.loads(validation.stdout)
            self.assertEqual(report["status"], "passed", report)
            shadcn_check = next(
                c for c in report["checks"]
                if c["name"] == "ui-stack-conformance" and c["status"] != "skipped"
                and "shadcn" in str(c["details"].get("official_pattern", "")).lower()
            )
            self.assertEqual(shadcn_check["status"], "passed", shadcn_check.get("warnings"))
            self.assertEqual(shadcn_check["details"].get("starter"), "react-shadcn-web")

    def test_vue_django_blueprint_generates_naive_starter(self):
        """vue-django 生成：Naive UI 2.x 官方范式（零 CSS 导入 + n-config-provider theme-overrides + zhCN/dateZhCN），validate 全 passed。"""
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-naive-starter-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "vue-django",
                "--name", "NaiveDemo", "--agents", "codex",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            frontend = Path(project) / "frontend"
            self.assertTrue((frontend / "src" / "main.ts").exists())
            self.assertTrue((frontend / "src" / "theme.ts").exists())
            self.assertTrue((frontend / "src" / "App.vue").exists())

            pkg = (frontend / "package.json").read_text(encoding="utf-8")
            self.assertIn('"naive-ui"', pkg)
            self.assertNotIn("babel-plugin-import", pkg)

            # 零 CSS 导入 + 全量注册（官方范式，禁止 naive-ui/dist/index.css）
            main_ts = (frontend / "src" / "main.ts").read_text(encoding="utf-8")
            self.assertNotIn("naive-ui/dist", main_ts)
            self.assertIn("app.use(naive)", main_ts)

            # 主题令牌集中 theme.ts（GlobalThemeOverrides）
            theme_ts = (frontend / "src" / "theme.ts").read_text(encoding="utf-8")
            self.assertIn("GlobalThemeOverrides", theme_ts)
            self.assertIn("themeOverrides", theme_ts)

            # n-config-provider :theme-overrides + 中文 locale
            app_vue = (frontend / "src" / "App.vue").read_text(encoding="utf-8")
            self.assertIn("n-config-provider", app_vue)
            self.assertIn("theme-overrides", app_vue)
            self.assertIn("zhCN", app_vue)
            self.assertIn("dateZhCN", app_vue)

            # 组件基线：n-* 组件（data-table / button / modal）
            views_text = "\n".join(
                f.read_text(encoding="utf-8") for f in (frontend / "src" / "views").rglob("*.vue")
            )
            self.assertIn("<n-data-table", views_text)
            self.assertIn("<n-button", views_text)
            self.assertIn("<n-modal", views_text)

            validation = self.run_script("validate.py", "--dir", project, "--json")
            self.assertEqual(validation.returncode, 0, validation.stderr)
            report = json.loads(validation.stdout)
            self.assertEqual(report["status"], "passed", report)
            naive_check = next(
                c for c in report["checks"]
                if c["name"] == "ui-stack-conformance" and c["status"] != "skipped"
                and "naive" in str(c["details"].get("official_pattern", "")).lower()
            )
            self.assertEqual(naive_check["status"], "passed", naive_check.get("warnings"))
            self.assertEqual(naive_check["details"].get("starter"), "vue-naive-web")



    def test_next_fullstack_blueprint_generates_shadcn_next_starter(self):
        """next-fullstack 生成：shadcn/ui v3 + Next.js App Router 官方范式（app/ + components/ + lib/ + components.json rsc），validate 全 passed。"""
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-shadcn-next-starter-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "next-fullstack",
                "--name", "NextDemo", "--agents", "codex",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            web = Path(project) / "apps" / "web"
            self.assertTrue((web / "components.json").exists())
            self.assertTrue((web / "app" / "globals.css").exists())
            self.assertTrue((web / "app" / "layout.tsx").exists())
            self.assertTrue((web / "components" / "ui" / "button.tsx").exists())
            self.assertTrue((web / "lib" / "utils.ts").exists())

            # Next.js + shadcn 官方依赖：@tailwindcss/postcss + next，无 babel-plugin-import
            pkg = (web / "package.json").read_text(encoding="utf-8")
            self.assertIn('"next"', pkg)
            self.assertIn("@tailwindcss/postcss", pkg)
            self.assertNotIn("babel-plugin-import", pkg)

            # 全局 CSS：@import "tailwindcss" + --primary / --radius 主题变量
            css = (web / "app" / "globals.css").read_text(encoding="utf-8")
            self.assertIn('@import "tailwindcss"', css)
            self.assertIn("--primary", css)
            self.assertIn("--radius", css)

            # components.json：RSC 模式 + app/globals.css + @/* 别名
            components_json = json.loads((web / "components.json").read_text(encoding="utf-8"))
            self.assertTrue(components_json.get("rsc"))
            self.assertEqual(components_json["tailwind"]["css"], "app/globals.css")

            # Next.js 官方范式：postcss 插件 + 路径别名 + 'use client' 交互组件
            postcss = (web / "postcss.config.mjs").read_text(encoding="utf-8")
            self.assertIn("@tailwindcss/postcss", postcss)
            tsconfig = (web / "tsconfig.json").read_text(encoding="utf-8")
            self.assertIn('"@/*"', tsconfig)
            dialog = (web / "components" / "ui" / "dialog.tsx").read_text(encoding="utf-8")
            self.assertIn("'use client'", dialog)

            # 语义类名 + {{PROJECT_NAME}} 渲染 + App Router 布局
            shell = (web / "components" / "app-shell.tsx").read_text(encoding="utf-8")
            self.assertIn("bg-primary", shell)
            self.assertIn("NextDemo", shell)
            layout = (web / "app" / "layout.tsx").read_text(encoding="utf-8")
            self.assertIn("NextDemo", layout)
            self.assertIn("metadata", layout)
            self.assertNotIn("{{PROJECT", shell + layout)

            validation = self.run_script("validate.py", "--dir", project, "--json")
            self.assertEqual(validation.returncode, 0, validation.stderr)
            report = json.loads(validation.stdout)
            self.assertEqual(report["status"], "passed", report)
            shadcn_check = next(
                c for c in report["checks"]
                if c["name"] == "ui-stack-conformance" and c["status"] != "skipped"
                and "shadcn" in str(c["details"].get("official_pattern", "")).lower()
            )
            self.assertEqual(shadcn_check["status"], "passed", shadcn_check.get("warnings"))
            self.assertEqual(shadcn_check["details"].get("starter"), "next-shadcn-web")



    # ─── P1: 官方 DEMO 对齐清单 + 构建期冒烟（build-smoke） ─────────────────

    def test_framework_gate_registers_official_demo_urls(self):
        """每个 UI 栈注册表条目都必须登记官方 demo 与文档链接（对齐清单依赖）。"""
        self.assertTrue(FRAMEWORK_CONSTRAINTS)
        for item in FRAMEWORK_CONSTRAINTS:
            with self.subTest(library=item.get("library")):
                demo = item.get("official_demo_url", "")
                docs = item.get("official_docs_url", "")
                self.assertTrue(
                    demo.startswith("http"),
                    f"{item.get('library')} 缺少 official_demo_url: {demo!r}",
                )
                self.assertTrue(
                    docs.startswith("http"),
                    f"{item.get('library')} 缺少 official_docs_url: {docs!r}",
                )

    def test_official_demo_checklist_rendered_in_readme_and_token_spec(self):
        """nuxt-ai-fullstack 生成：README / DESIGN / design-token-spec 都带官方 DEMO 对齐内容。"""
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-official-demo-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "nuxt-ai-fullstack",
                "--name", "MatchCV", "--agents", "codex,cursor",
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            readme = (Path(project) / "README.md").read_text(encoding="utf-8")
            self.assertIn("与官方 DEMO 对齐", readme)
            self.assertIn("github.com/nuxt-ui-templates/dashboard", readme)
            self.assertIn("ui.nuxt.com", readme)
            self.assertIn("ui-stack-conformance", readme)
            self.assertIn("starter 目录已生成", readme)

            spec = (Path(project) / "docs" / "00-research" / "design-token-spec.md").read_text(encoding="utf-8")
            self.assertIn("与官方 DEMO 对齐清单", spec)
            self.assertIn("官方 DEMO / 模板", spec)
            self.assertIn("github.com/nuxt-ui-templates/dashboard", spec)

            design = (Path(project) / "docs" / "DESIGN.md").read_text(encoding="utf-8")
            self.assertIn("官方 DEMO / 模板", design)
            self.assertIn("github.com/nuxt-ui-templates/dashboard", design)

    def test_official_demo_alignment_covers_all_ui_stacks(self):
        """6 个 UI 栈 Blueprint 生成的 README 都渲染对应官方 demo 链接。"""
        cases = {
            "nuxt-ai-fullstack": "github.com/nuxt-ui-templates/dashboard",
            "uni-app-nitro": "vant-ui.github.io/vant",
            "vue-element-plus-nitro": "element-plus.org",
            "react-springboot": "ant.design",
            "react-fastapi": "ui.shadcn.com",
            "vue-django": "naiveui.com",
            "next-fullstack": "ui.shadcn.com",
        }
        for blueprint_id, url_fragment in cases.items():
            with self.subTest(blueprint=blueprint_id):
                with tempfile.TemporaryDirectory(prefix=f"ai-bootstrap-demo-{blueprint_id}-") as project:
                    result = self.run_script(
                        "generate.py", "--dir", project, "--blueprint", blueprint_id,
                        "--name", "Demo", "--agents", "codex",
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    readme = (Path(project) / "README.md").read_text(encoding="utf-8")
                    self.assertIn("与官方 DEMO 对齐", readme)
                    self.assertIn(url_fragment, readme)

    def test_build_smoke_plan_resolves_workspace_targets(self):
        """build-smoke --plan：nuxt 单仓根只 install，各 app 探测到构建脚本。"""
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-buildsmoke-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "nuxt-ai-fullstack",
                "--name", "MatchCV", "--agents", "codex,cursor",
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            smoke = self.run_script("build_smoke.py", "--dir", project, "--plan", "--json")
            self.assertEqual(smoke.returncode, 0, smoke.stderr)
            report = json.loads(smoke.stdout)
            self.assertEqual(report["package_manager"], "pnpm")
            self.assertTrue(report["plan"])
            by_dir = {t["dir"]: t for t in report["targets"]}

            self.assertIn(".", by_dir)
            root = by_dir["."]
            self.assertTrue(root["is_workspace_root"])
            self.assertIsNone(root["build_script"])
            self.assertEqual(root["build"]["state"], "skip")

            for app_dir in ("apps/app-web-hr", "apps/app-web-platform", "apps/app-web-server"):
                self.assertIn(app_dir, by_dir, f"缺少 target {app_dir}")
                self.assertEqual(by_dir[app_dir]["build_script"], "build")
            self.assertEqual(by_dir["apps/app-web-hr"]["build"]["cmd"], "pnpm run build")

    def test_build_smoke_plan_on_standalone_and_uni(self):
        """build-smoke --plan：独立 frontend 目标 + uni-app build:h5 脚本探测。"""
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-buildsmoke-react-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "react-fastapi",
                "--name", "Demo", "--agents", "codex",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            smoke = self.run_script("build_smoke.py", "--dir", project, "--plan", "--json")
            report = json.loads(smoke.stdout)
            targets = {t["dir"]: t for t in report["targets"]}
            self.assertIn("frontend", targets)
            self.assertEqual(targets["frontend"]["build_script"], "build")
            self.assertEqual(targets["frontend"]["build"]["cmd"], "pnpm run build")

        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-buildsmoke-uni-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "uni-app-nitro",
                "--name", "Demo", "--agents", "codex",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            smoke = self.run_script("build_smoke.py", "--dir", project, "--plan", "--json")
            report = json.loads(smoke.stdout)
            targets = {t["dir"]: t for t in report["targets"]}
            self.assertIn("apps/mobile", targets)
            self.assertEqual(targets["apps/mobile"]["build_script"], "build:h5")
            self.assertEqual(targets["apps/mobile"]["build"]["cmd"], "pnpm run build:h5")
            # uni-app H5 构建必需官方 index.html 入口（vite-plugin-uni 解析 entry module）
            index_html = Path(project) / "apps" / "mobile" / "index.html"
            self.assertTrue(index_html.exists(), "uni-app starter 缺少官方 index.html H5 入口")
            self.assertIn("src/main.ts", index_html.read_text(encoding="utf-8"))

    def test_build_smoke_script_detection_helpers(self):
        """build-smoke 的脚本探测 / 包管理器探测 / manifest 解析单测。"""
        from build_smoke import build_script_for, detect_package_manager, manifest_targets

        self.assertEqual(build_script_for({"scripts": {"build": "vite build"}}), "build")
        self.assertEqual(build_script_for({"scripts": {"build:h5": "uni build"}}), "build:h5")
        self.assertEqual(build_script_for({"scripts": {"build:prod": "vite build"}}), "build:prod")
        self.assertEqual(build_script_for({"scripts": {"dev": "vite"}}), None)
        self.assertEqual(build_script_for({}), None)
        self.assertEqual(build_script_for(None), None)

        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-pm-") as tmp:
            root = Path(tmp)
            self.assertEqual(detect_package_manager(root), "pnpm")
            (root / "package-lock.json").write_text("{}", encoding="utf-8")
            self.assertEqual(detect_package_manager(root), "npm")
            (root / "pnpm-lock.yaml").write_text("", encoding="utf-8")
            self.assertEqual(detect_package_manager(root), "pnpm")
            self.assertEqual(detect_package_manager(root, prefer="yarn"), "yarn")

        manifest = {"manifest": {"starter": {"template_dirs": [
            {"dir": "react-shadcn-web", "target": "frontend"},
        ]}}}
        self.assertEqual(
            manifest_targets(manifest),
            [{"starter": "react-shadcn-web", "target": "frontend"}],
        )
        self.assertEqual(manifest_targets(None), [])


    def test_readme_description_derives_from_blueprint(self):
        """未传 --description 时，README 简介默认采用 Blueprint 的 description，避免空洞占位。"""
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-desc-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "nuxt-ai-fullstack",
                "--name", "DescCheck", "--agents", "codex",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            readme = (Path(project) / "README.md").read_text(encoding="utf-8")
            self.assertIn("Nuxt 4 + Nuxt UI", readme)
            self.assertNotIn("AI Native Project", readme)

        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-desc-2-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "nuxt-ai-fullstack",
                "--name", "DescCheck", "--description", "My custom intro", "--agents", "codex",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            readme = (Path(project) / "README.md").read_text(encoding="utf-8")
            self.assertIn("My custom intro", readme)

    def test_layout_contract_single_source_in_design(self):
        """目录契约单一来源：职责表只在 DESIGN.md，README/PROFILE 引用而不复制。"""
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-layout-src-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "nuxt-ai-fullstack",
                "--name", "SingleSource", "--agents", "codex",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            readme = (Path(project) / "README.md").read_text(encoding="utf-8")
            profile = (Path(project) / "docs" / "PROJECT_PROFILE.md").read_text(encoding="utf-8")
            design = (Path(project) / "docs" / "DESIGN.md").read_text(encoding="utf-8")
            self.assertNotIn("| 目录 | 职责 |", readme)
            self.assertNotIn("| 目录 | 职责 |", profile)
            self.assertIn("| 目录 | 职责 |", design)
            self.assertIn("docs/DESIGN.md", readme)
            self.assertIn("唯一来源", profile)

    def test_manifest_records_starter_landing_status(self):
        """manifest 如实记录 starter 落地状态：applied / skipped / partial。"""
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-manifest-status-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "nuxt-ai-fullstack",
                "--name", "MobileCoach", "--agents", "codex",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = load_yaml_text(
                (Path(project) / ".ai-bootstrap" / "bootstrap-manifest.yaml").read_text(encoding="utf-8")
            )
            starter = manifest["manifest"]["starter"]
            self.assertEqual(starter["status"], "applied")
            self.assertEqual(len(starter["applied_dirs"]), 4)
            self.assertEqual(starter["missing_dirs"], [])

        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-manifest-no-starter-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "nuxt-ai-fullstack",
                "--no-starter", "--agents", "codex",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = load_yaml_text(
                (Path(project) / ".ai-bootstrap" / "bootstrap-manifest.yaml").read_text(encoding="utf-8")
            )
            starter = manifest["manifest"]["starter"]
            self.assertEqual(starter["status"], "skipped")
            self.assertEqual(starter["applied_dirs"], [])

        # 声明了不存在的模板目录时：status=partial 且如实列出 missing/applied
        from generate import copy_starter_template, generate_manifest

        class _Args:
            starter = None
            dry_run = True
            force = False
            name = "PartialProj"
            dir = "/tmp/partial-proj"

        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-manifest-partial-") as project:
            args = _Args()
            blueprint = {
                "id": "custom", "version": "1.0.0", "name": "Custom", "tags": [],
                "description": "partial starter test", "stack": {}, "architecture": {},
                "starter": {
                    "enabled": True,
                    "mode": "mock-first",
                    "template_dirs": [
                        {"dir": "nuxt-app-hr", "target": "apps/app-web-hr"},
                        {"dir": "missing-template-dir", "target": "apps/missing"},
                    ],
                },
            }
            generated: list = []
            result = copy_starter_template(Path(project), blueprint, args, generated, True, {})
            self.assertEqual(result["applied"], ["nuxt-app-hr"])
            self.assertEqual(result["missing"], ["missing-template-dir"])
            manifest = generate_manifest(
                args, blueprint, [], {"AGENT_COUNT": 1}, "test", starter_result=result
            )
            starter = manifest["manifest"]["starter"]
            self.assertEqual(starter["status"], "partial")
            self.assertEqual(starter["applied_dirs"], ["nuxt-app-hr"])
            self.assertEqual(starter["missing_dirs"], ["missing-template-dir"])

    def test_fonts_skipped_by_default_and_opt_in_via_flag(self):
        """字体包默认跳过（国内网络友好），--fonts 显式开启后才引入依赖与 import。"""
        # 默认：跳过字体（nuxt 与 naive-ui 两个入口）
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-fonts-default-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "nuxt-ai-fullstack",
                "--name", "MatchCV", "--agents", "codex",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            for app in ("app-web-hr", "app-web-platform"):
                pkg = (Path(project) / f"apps/{app}/package.json").read_text(encoding="utf-8")
                self.assertNotIn("@fontsource-variable/inter", pkg)
                main_css = (Path(project) / f"apps/{app}/app/assets/css/main.css").read_text(encoding="utf-8")
                self.assertNotIn("@import '@fontsource-variable/inter'", main_css)
                self.assertIn("--fonts", main_css)  # 只保留说明注释
                fonts_ts = (Path(project) / f"apps/{app}/app/plugins/fonts.ts").read_text(encoding="utf-8")
                self.assertNotIn("import '@fontsource-variable/inter'", fonts_ts)
            validation = self.run_script("validate.py", "--dir", project, "--json")
            self.assertEqual(validation.returncode, 0, validation.stderr)
            report = json.loads(validation.stdout)
            self.assertEqual(report["status"], "passed")
            visual = next(c for c in report["checks"] if c["name"] == "demo-visual-baseline")
            self.assertEqual(visual["status"], "passed")
            for app_detail in visual["details"]["apps"]:
                self.assertFalse(app_detail["fonts_loaded"])

        # --fonts：引入 @fontsource-variable/inter，字体证据恢复
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-fonts-on-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "nuxt-ai-fullstack",
                "--name", "MatchCV", "--agents", "codex", "--fonts",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            for app in ("app-web-hr", "app-web-platform"):
                pkg = (Path(project) / f"apps/{app}/package.json").read_text(encoding="utf-8")
                self.assertIn("@fontsource-variable/inter", pkg)
                main_css = (Path(project) / f"apps/{app}/app/assets/css/main.css").read_text(encoding="utf-8")
                self.assertIn("@import '@fontsource-variable/inter'", main_css)
                self.assertIn("'Inter Variable'", main_css)
            validation = self.run_script("validate.py", "--dir", project, "--json")
            self.assertEqual(validation.returncode, 0, validation.stderr)
            visual = next(c for c in json.loads(validation.stdout)["checks"] if c["name"] == "demo-visual-baseline")
            self.assertEqual(visual["status"], "passed")
            for app_detail in visual["details"]["apps"]:
                self.assertTrue(app_detail["fonts_loaded"])

        # naive-ui（vue-django）同样默认跳过 vfonts
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-fonts-naive-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "vue-django",
                "--name", "MatchCV", "--agents", "codex",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            pkg = (Path(project) / "frontend" / "package.json").read_text(encoding="utf-8")
            self.assertNotIn("vfonts", pkg)
            main_ts = (Path(project) / "frontend" / "src" / "main.ts").read_text(encoding="utf-8")
            self.assertNotIn("import 'vfonts/", main_ts)
            self.assertIn("--fonts", main_ts)

    def test_fonts_evidence_accepts_main_css_fontsource_import(self):
        """demo-visual-baseline：字体为可选基线；main.css 内联 @import fontsource 视为字体证据，
        两种证据都缺时只记录 fonts_note（不再计为缺失），核心基线缺失仍报 warning。"""
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-fonts-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "nuxt-ai-fullstack",
                "--name", "MatchCV", "--agents", "codex", "--fonts",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            for app in ("app-web-hr", "app-web-platform"):
                fonts_plugin = Path(project) / f"apps/{app}/app/plugins/fonts.ts"
                fonts_plugin.unlink()  # 模拟 MEMORY 决策 5 的合法优化：只保留 main.css import

            validation = self.run_script("validate.py", "--dir", project, "--json")
            self.assertEqual(validation.returncode, 0, validation.stderr)
            report = json.loads(validation.stdout)
            visual = next(c for c in report["checks"] if c["name"] == "demo-visual-baseline")
            self.assertEqual(visual["status"], "passed")

            # 反向：两种字体证据都没有时不再计为缺失（字体可选），核心基线缺失才报 warning
            for app in ("app-web-hr", "app-web-platform"):
                main_css = Path(project) / f"apps/{app}/app/assets/css/main.css"
                text = main_css.read_text(encoding="utf-8").replace(
                    "@import '@fontsource-variable/inter';", ""
                )
                main_css.write_text(text, encoding="utf-8")
            validation2 = self.run_script("validate.py", "--dir", project, "--json")
            report2 = json.loads(validation2.stdout)
            visual2 = next(c for c in report2["checks"] if c["name"] == "demo-visual-baseline")
            self.assertEqual(visual2["status"], "passed")
            for app_detail in visual2["details"]["apps"]:
                self.assertFalse(app_detail["fonts_loaded"])
                self.assertIn("fonts_note", app_detail)

            # 核心基线（layouts）缺失时仍报 warning
            (Path(project) / "apps/app-web-hr/app/layouts").rename(
                Path(project) / "apps/app-web-hr/app/layouts.bak"
            )
            validation3 = self.run_script("validate.py", "--dir", project, "--json")
            report3 = json.loads(validation3.stdout)
            visual3 = next(c for c in report3["checks"] if c["name"] == "demo-visual-baseline")
            self.assertEqual(visual3["status"], "warning")
            self.assertTrue(any("layouts" in w for w in visual3["warnings"]))


    # ─── P1.5: Java/Maven 后端 starter + vue-springboot Blueprint ──────────────

    def test_react_springboot_generates_backend_starter(self):
        """react-springboot 生成 backend/ Spring Boot Maven 工程（此前只有 frontend）。"""
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-java-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "react-springboot",
                "--name", "MatchCV", "--agents", "codex",
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            backend = Path(project) / "backend"
            self.assertTrue((backend / "pom.xml").exists())
            self.assertTrue((backend / "src" / "main" / "java" / "com" / "aibootstrap" / "server" / "ServerApplication.java").exists())
            self.assertTrue((backend / "src" / "main" / "resources" / "application.yml").exists())
            self.assertTrue((backend / "src" / "main" / "java" / "com" / "aibootstrap" / "server" / "config" / "SecurityConfig.java").exists())
            self.assertTrue((backend / "Dockerfile").exists())

            pom = (backend / "pom.xml").read_text(encoding="utf-8")
            self.assertIn("spring-boot-starter-parent", pom)
            self.assertIn("<java.version>17</java.version>", pom)
            self.assertIn("matchcv-server", pom)

            # 前端 tsconfig 自包含（不依赖 workspace 根 tsconfig.base.json，任意挂载深度可构建）
            tsconfig = (Path(project) / "frontend" / "tsconfig.json").read_text(encoding="utf-8")
            self.assertNotIn('"extends"', tsconfig)

            readme = (Path(project) / "README.md").read_text(encoding="utf-8")
            self.assertIn("与官方 DEMO 对齐", readme)
            self.assertIn("ant.design", readme)

    def test_vue_springboot_blueprint_generates_fullstack(self):
        """vue-springboot（Vue3 + Element Plus + Spring Boot）生成前后端并渲染官方对齐清单。"""
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-vue-java-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "vue-springboot",
                "--name", "MatchCV", "--agents", "codex",
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            self.assertTrue((Path(project) / "frontend" / "package.json").exists())
            self.assertTrue((Path(project) / "frontend" / "src" / "main.ts").exists())
            self.assertTrue((Path(project) / "backend" / "pom.xml").exists())
            self.assertTrue((Path(project) / "backend" / "src" / "main" / "java").exists())

            readme = (Path(project) / "README.md").read_text(encoding="utf-8")
            self.assertIn("与官方 DEMO 对齐", readme)
            self.assertIn("element-plus.org", readme)
            self.assertIn("ui-stack-conformance", readme)

            design = (Path(project) / "docs" / "DESIGN.md").read_text(encoding="utf-8")
            self.assertIn("Element Plus 2.x", design)
            self.assertIn("官方 DEMO / 模板", design)

            spec = (Path(project) / "docs" / "00-research" / "design-token-spec.md").read_text(encoding="utf-8")
            self.assertIn("--el-*", spec)
            self.assertIn("与官方 DEMO 对齐清单", spec)

    def test_build_smoke_plan_resolves_maven_target(self):
        """build_smoke --plan 识别 backend/ Maven 目标（mvn package），前端/后端并列。"""
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-maven-plan-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "react-springboot",
                "--name", "MatchCV", "--agents", "codex",
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            smoke = self.run_script("build_smoke.py", "--dir", project, "--plan", "--json")
            self.assertEqual(smoke.returncode, 0, smoke.stderr)
            data = json.loads(smoke.stdout)
            targets = {t["dir"]: t for t in data["targets"]}
            self.assertIn("frontend", targets)
            self.assertIn("backend", targets)
            self.assertEqual(targets["backend"]["build_script"], "mvn package")
            self.assertEqual(targets["frontend"]["build_script"], "build")

    def test_spring_boot_starter_renders_slug_into_pom(self):
        """后端 pom 使用 {{PROJECT_SLUG}}-server 作为 artifactId（不同项目名可区分）。"""
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-java-slug-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "vue-springboot",
                "--name", "MyCool App", "--agents", "codex",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            pom = (Path(project) / "backend" / "pom.xml").read_text(encoding="utf-8")
            self.assertIn("<artifactId>mycool-app-server</artifactId>", pom)



    def test_springboot_governance_docs_pin_jdk17_and_maven(self):
        """法则文档（AGENTS/PROFILE/DESIGN/README）必须写入 JDK 17 + Maven 环境基线，
        指导 AI Agent 安装环境时参考（Spring Boot 3.x 用 JDK 17 最稳、必须支持 Maven）。"""
        for blueprint_id in ("react-springboot", "vue-springboot"):
            with self.subTest(blueprint=blueprint_id):
                with tempfile.TemporaryDirectory(prefix="ai-bootstrap-jdk-") as project:
                    result = self.run_script(
                        "generate.py", "--dir", project, "--blueprint", blueprint_id,
                        "--name", "MatchCV", "--agents", "codex",
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    for doc in ("AGENTS.md", "README.md", "docs/PROJECT_PROFILE.md", "docs/DESIGN.md"):
                        text = (Path(project) / doc).read_text(encoding="utf-8")
                        self.assertIn("JDK 17", text, f"{doc} missing JDK 17")
                        self.assertIn("Maven", text, f"{doc} missing Maven")
                        self.assertIn("mvn -f backend/pom.xml", text, f"{doc} missing maven command")
                        self.assertIn("java.version", text, f"{doc} missing java.version pin")
                        self.assertNotIn("{{", text)

    def test_springboot_environment_baseline_is_spring_specific(self):
        """环境基线按栈派生：非 Java 后端不出现 JDK/Maven 指导，前端基线仍存在。"""
        with tempfile.TemporaryDirectory(prefix="ai-bootstrap-env-node-") as project:
            result = self.run_script(
                "generate.py", "--dir", project, "--blueprint", "nuxt-ai-fullstack",
                "--name", "MatchCV", "--agents", "codex",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            agents = (Path(project) / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("Node.js 20+", agents)
            self.assertNotIn("JDK 17", agents)
            self.assertNotIn("mvn -f", agents)
            readme = (Path(project) / "README.md").read_text(encoding="utf-8")
            self.assertIn("Node.js 20+", readme)

if __name__ == "__main__":
    unittest.main()
