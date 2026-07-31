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
from yaml_utils import load_yaml_text  # noqa: E402


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
            "vue-django": ("vue", "postgres"),
            "go-microservice": ("none", "postgres"),
            "rust-axum-api": ("none", "sqlite"),
            "python-ml-service": ("none", "postgres"),
        }
        for blueprint_id, (frontend, database) in expected.items():
            with self.subTest(blueprint=blueprint_id):
                blueprint = load_blueprint(blueprint_id)
                self.assertIsNotNone(blueprint)
                self.assertEqual(blueprint["stack"]["frontend"]["framework"], frontend)
                self.assertEqual(blueprint["stack"]["database"]["primary"], database)
                self.assertIsInstance(blueprint["tags"], list)

        ml = load_blueprint("python-ml-service")
        self.assertEqual(ml["stack"]["backend"]["framework"], "fastapi")
        self.assertEqual(ml["stack"]["ml"]["framework"], "pytorch")

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
            "vue-django": "typescript",
            "go-microservice": "go",
            "rust-axum-api": "rust",
            "python-ml-service": "python",
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


if __name__ == "__main__":
    unittest.main()
