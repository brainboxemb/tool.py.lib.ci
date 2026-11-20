from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "change_scope.py"
SPEC = spec_from_file_location("tool_py_lib_ci_change_scope", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"could not load {SCRIPT}")
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

SHA_A = "a" * 40
SHA_B = "b" * 40
ZERO_SHA = "0" * 40


class ChangeScopeTests(unittest.TestCase):
    def test_non_empty_docs_tree_is_docs_only(self):
        self.assertEqual(
            MODULE.classify_paths(
                ["docs/plan.md", "docs/design/architecture.md"]
            ),
            "docs-only",
        )

    def test_empty_change_set_fails_safe_to_full(self):
        self.assertEqual(MODULE.classify_paths([]), "full")

    def test_mixed_change_set_is_full(self):
        self.assertEqual(
            MODULE.classify_paths(["docs/plan.md", "src/package.py"]),
            "full",
        )

    def test_paths_outside_docs_are_full(self):
        for path in (
            "README.md",
            "AGENTS.md",
            ".github/workflows/ci.yml",
            "docs-file.md",
        ):
            with self.subTest(path=path):
                self.assertEqual(MODULE.classify_paths([path]), "full")

    def test_nul_delimited_path_file_is_read_exactly(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "changed"
            path.write_bytes(b"docs/plan.md\0docs/design.md\0")
            self.assertEqual(
                MODULE.read_nul_paths(path),
                ["docs/plan.md", "docs/design.md"],
            )

    def test_pull_request_uses_valid_pull_base(self):
        self.assertEqual(
            MODULE.comparison_base(
                event_name="pull_request",
                source_sha_input="",
                pull_base_sha=SHA_A,
                push_before_sha="",
                push_forced=False,
            ),
            SHA_A,
        )

    def test_normal_push_uses_valid_before_sha(self):
        self.assertEqual(
            MODULE.comparison_base(
                event_name="push",
                source_sha_input="",
                pull_base_sha="",
                push_before_sha=SHA_B,
                push_forced=False,
            ),
            SHA_B,
        )

    def test_unsafe_context_fails_safe_to_no_comparison(self):
        cases = (
            dict(
                event_name="push",
                source_sha_input="",
                pull_base_sha="",
                push_before_sha=SHA_B,
                push_forced=True,
            ),
            dict(
                event_name="push",
                source_sha_input="",
                pull_base_sha="",
                push_before_sha=ZERO_SHA,
                push_forced=False,
            ),
            dict(
                event_name="push",
                source_sha_input="override",
                pull_base_sha="",
                push_before_sha=SHA_B,
                push_forced=False,
            ),
            dict(
                event_name="pull_request",
                source_sha_input="override",
                pull_base_sha=SHA_A,
                push_before_sha="",
                push_forced=False,
            ),
            dict(
                event_name="workflow_dispatch",
                source_sha_input="",
                pull_base_sha=SHA_A,
                push_before_sha=SHA_B,
                push_forced=False,
            ),
            dict(
                event_name="push",
                source_sha_input="",
                pull_base_sha="",
                push_before_sha="not-a-sha",
                push_forced=False,
            ),
        )
        for values in cases:
            with self.subTest(values=values):
                self.assertIsNone(MODULE.comparison_base(**values))


if __name__ == "__main__":
    unittest.main()
