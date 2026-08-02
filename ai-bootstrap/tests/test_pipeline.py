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
            self.assertIn("apps/web", readme_text)
            self.assertIn("pnpm install", readme_text)
            self.assertIn("pnpm dev", readme_text)
            self.assertIn("pnpm test", readme_text)
            design_text = (Path(project) / "docs" / "DESIGN.md").read_text(encoding="utf-8")
            self.assertIn("项目目录契约", design_text)
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
                "apps/app-web-platform/app/components/AppSidebar.vue",
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



if __name__ == "__main__":
    unittest.main()
