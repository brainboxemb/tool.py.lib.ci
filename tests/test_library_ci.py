from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import os
import tempfile
import textwrap
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "library_ci.py"
SPEC = spec_from_file_location("tool_py_lib_ci", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"could not load {SCRIPT}")
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class LibraryCITests(unittest.TestCase):
    def make_consumer(self, root: Path, *, failing_test: bool = False) -> Path:
        repo = root / "consumer"
        (repo / "src" / "sample_consumer").mkdir(parents=True)
        (repo / "tests").mkdir()
        (repo / "pyproject.toml").write_text(
            textwrap.dedent(
                """
                [build-system]
                requires = ["setuptools>=68", "wheel"]
                build-backend = "setuptools.build_meta"

                [project]
                name = "sample-consumer"
                version = "0.1.0"
                dependencies = ["packaging>=23"]

                [tool.setuptools.packages.find]
                where = ["src"]
                """
            ).strip()
            + "\n",
            encoding="utf-8",
        )
        (repo / "src" / "sample_consumer" / "__init__.py").write_text(
            'VALUE = "installed-wheel"\n',
            encoding="utf-8",
        )
        assertion = "self.fail('expected failure')" if failing_test else (
            "self.assertEqual(sample_consumer.VALUE, 'installed-wheel')"
        )
        (repo / "tests" / "test_package.py").write_text(
            textwrap.dedent(
                f"""
                import pathlib
                import unittest

                import packaging
                import sample_consumer


                class PackageTests(unittest.TestCase):
                    def test_installed_package(self):
                        {assertion}
                        source = pathlib.Path(sample_consumer.__file__).resolve()
                        repo = pathlib.Path({str(repo)!r}).resolve()
                        self.assertFalse(source.is_relative_to(repo))
                        self.assertTrue(packaging.__version__)


                if __name__ == "__main__":
                    unittest.main()
                """
            ).strip()
            + "\n",
            encoding="utf-8",
        )
        return repo

    def test_single_wheel_requires_exactly_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(MODULE.PipelineError):
                MODULE.single_wheel(root)
            (root / "one.whl").write_bytes(b"x")
            self.assertEqual(MODULE.single_wheel(root).name, "one.whl")
            (root / "two.whl").write_bytes(b"x")
            with self.assertRaises(MODULE.PipelineError):
                MODULE.single_wheel(root)

    def test_test_command_expands_placeholders(self):
        command = MODULE.test_command(
            "{python} -c 'print(1)' {repo}",
            python=Path("/venv/python"),
            repo=Path("/consumer"),
        )
        self.assertEqual(
            command,
            ["/venv/python", "-c", "print(1)", "/consumer"],
        )

    def test_default_test_command_uses_clean_python_and_absolute_tests(self):
        command = MODULE.test_command(
            "",
            python=Path("/venv/python"),
            repo=Path("/consumer"),
        )
        self.assertEqual(command[0], "/venv/python")
        self.assertIn("/consumer/tests", command)

    def test_pipeline_builds_installs_dependencies_and_tests_installed_wheel(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = self.make_consumer(root)
            wheel = MODULE.run_pipeline(repo, root / "work")
            self.assertTrue(wheel.is_file())
            self.assertEqual(wheel.suffix, ".whl")

    def test_failing_consumer_test_propagates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = self.make_consumer(root, failing_test=True)
            with self.assertRaises(MODULE.PipelineError) as caught:
                MODULE.run_pipeline(repo, root / "work")
            self.assertEqual(caught.exception.stage, "test")

    def test_build_failure_propagates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "consumer"
            repo.mkdir()
            with self.assertRaises(MODULE.PipelineError) as caught:
                MODULE.build_wheel(repo, root / "work")
            self.assertEqual(caught.exception.stage, "build")

    def test_install_failure_propagates(self):
        completed = mock.Mock(returncode=4)
        with mock.patch.object(MODULE.subprocess, "run", return_value=completed):
            with self.assertRaises(MODULE.PipelineError) as caught:
                MODULE.install_wheel(
                    Path("/venv/python"),
                    Path("/bad.whl"),
                    work=Path("/tmp"),
                )
        self.assertEqual(caught.exception.stage, "install")

    def test_public_workflow_has_no_cache_scons_or_cad_ci(self):
        workflow = (
            ROOT / ".github" / "workflows" / "reusable-ci.yml"
        ).read_text(encoding="utf-8").lower()
        forbidden = (
            "actions/cache",
            "scons",
            ".cad-ci",
            ".cache/cad-ci",
            "tool.cad.ci",
            "lib.py.cad.ci",
        )
        for value in forbidden:
            with self.subTest(value=value):
                self.assertNotIn(value, workflow)

    def test_reusable_workflow_uses_called_tool_revision(self):
        workflow = (
            ROOT / ".github" / "workflows" / "reusable-ci.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("job.workflow_repository", workflow)
        self.assertIn("job.workflow_sha", workflow)
        self.assertIn("PY_LIB_CI_SOURCE_SHA", workflow)


if __name__ == "__main__":
    unittest.main()
