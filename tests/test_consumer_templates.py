"""Contract tests for Python-library consumer workflow templates."""

from pathlib import Path
import json
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = ROOT / "templates"
WORKFLOW_ROOT = TEMPLATE_ROOT / "github" / "workflows"
MARKER = "TOOL_PY_LIB_CI_RELEASE_SHA"


def load_yaml(path: Path) -> dict:
    value = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    if not isinstance(value, dict):
        raise AssertionError(f"{path}: expected mapping")
    return value


class ConsumerTemplateTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(
            (TEMPLATE_ROOT / "manifest.json").read_text(encoding="utf-8")
        )
        self.templates = self.manifest["templates"]

    def test_manifest_covers_every_template_and_versions_each_one(self):
        actual = {
            str(path.relative_to(TEMPLATE_ROOT))
            for path in WORKFLOW_ROOT.glob("*.yml")
        }
        self.assertEqual(self.manifest["schema"], 1)
        self.assertEqual(set(self.templates), actual)
        for relative, entry in self.templates.items():
            with self.subTest(template=relative):
                self.assertRegex(entry["id"], r"^tool\.py\.lib\.ci/[a-z0-9-]+$")
                self.assertIsInstance(entry["version"], int)
                self.assertGreater(entry["version"], 0)

    def test_template_headers_match_manifest(self):
        for relative, entry in self.templates.items():
            text = (TEMPLATE_ROOT / relative).read_text(encoding="utf-8")
            with self.subTest(template=relative):
                self.assertIn(f"# template: {entry['id']}", text)
                self.assertIn(f"# template-version: {entry['version']}", text)

    def test_templates_use_one_immutable_release_marker(self):
        for relative in self.templates:
            text = (TEMPLATE_ROOT / relative).read_text(encoding="utf-8")
            with self.subTest(template=relative):
                self.assertEqual(text.count(MARKER), 2)
                self.assertIn("brainboxemb/tool.py.lib.ci/", text)

    def test_ci_template_calls_only_public_reusable_ci(self):
        wf = load_yaml(WORKFLOW_ROOT / "ci.yml")
        job = wf["jobs"]["library-ci"]
        self.assertNotIn("runs-on", job)
        self.assertEqual(
            job["uses"],
            "brainboxemb/tool.py.lib.ci/.github/workflows/reusable-ci.yml@"
            + MARKER,
        )
        self.assertEqual(wf["permissions"]["contents"], "read")

    def test_release_template_calls_only_public_reusable_release(self):
        wf = load_yaml(WORKFLOW_ROOT / "release.yml")
        job = wf["jobs"]["release"]
        self.assertNotIn("runs-on", job)
        self.assertEqual(
            job["uses"],
            "brainboxemb/tool.py.lib.ci/.github/workflows/reusable-release.yml@"
            + MARKER,
        )
        self.assertEqual(job["permissions"]["contents"], "write")
        self.assertEqual(job["permissions"]["issues"], "write")
        self.assertNotIn("validator_path", job["with"])

    def test_consumer_templates_do_not_copy_generic_implementation(self):
        forbidden = (
            "actions/checkout@",
            "actions/setup-python@",
            "gh api",
            "pip install",
            "git tag",
            "git push",
            "publish_release.py",
            "release_command.py",
        )
        for relative in self.templates:
            text = (TEMPLATE_ROOT / relative).read_text(encoding="utf-8").lower()
            with self.subTest(template=relative):
                for value in forbidden:
                    self.assertNotIn(value, text)

    def test_templates_do_not_encode_forge_or_cad_policy(self):
        forbidden = ("forge", "solidcraft", "cad-ci", "scons")
        for relative in self.templates:
            text = (TEMPLATE_ROOT / relative).read_text(encoding="utf-8").lower()
            with self.subTest(template=relative):
                for value in forbidden:
                    self.assertNotIn(value, text)


if __name__ == "__main__":
    unittest.main()
