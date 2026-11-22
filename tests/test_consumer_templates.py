"""Contract tests for Python-library consumer workflow templates."""

from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = ROOT / "templates"
WORKFLOW_ROOT = TEMPLATE_ROOT / "github" / "workflows"
MARKER = "TOOL_PY_LIB_CI_RELEASE_SHA"


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

    def test_templates_use_one_release_marker_in_comment_and_reference(self):
        for relative in self.templates:
            text = (TEMPLATE_ROOT / relative).read_text(encoding="utf-8")
            with self.subTest(template=relative):
                self.assertEqual(text.count(MARKER), 2)
                self.assertIn("brainboxemb/tool.py.lib.ci/", text)

    def test_ci_template_is_only_a_public_reusable_call(self):
        text = (WORKFLOW_ROOT / "ci.yml").read_text(encoding="utf-8")
        self.assertIn(
            "uses: brainboxemb/tool.py.lib.ci/.github/workflows/"
            "reusable-ci.yml@" + MARKER,
            text,
        )
        self.assertIn("contents: read", text)
        self.assertNotIn("runs-on:", text)

    def test_release_template_is_only_a_public_reusable_call(self):
        text = (WORKFLOW_ROOT / "release.yml").read_text(encoding="utf-8")
        self.assertIn(
            "uses: brainboxemb/tool.py.lib.ci/.github/workflows/"
            "reusable-release.yml@" + MARKER,
            text,
        )
        self.assertIn("contents: write", text)
        self.assertIn("issues: write", text)
        self.assertNotIn("runs-on:", text)
        self.assertNotIn("\n      validator_path:", text)

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
