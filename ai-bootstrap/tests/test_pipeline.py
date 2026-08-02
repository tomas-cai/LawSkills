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
            self.assertIn("## 3. 语义颜色", token_text)
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


if __name__ == "__main__":
    unittest.main()
