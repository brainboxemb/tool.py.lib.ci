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
        for path in ("README.md", "AGENTS.md", ".github/workflows/ci.yml", "docs-file.md"):
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


if __name__ == "__main__":
    unittest.main()
