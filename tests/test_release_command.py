from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
SCRIPT = SCRIPTS / "release_command.py"
SPEC = spec_from_file_location("release_command", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"could not load {SCRIPT}")
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ReleaseCommandTests(unittest.TestCase):
    def test_parse_exact_release_command(self):
        version, sha = MODULE.parse_release_command(
            "/release v1.2.3 " + "a" * 40
        )
        self.assertEqual(version, "1.2.3")
        self.assertEqual(sha, "a" * 40)

    def test_reject_extra_missing_or_malformed_command_parts(self):
        invalid = (
            "/release",
            "/release 1.2.3 " + "a" * 40,
            "/release v1.2 " + "a" * 40,
            "/release v1.2.3 main",
            "/release v1.2.3 " + "a" * 40 + " extra",
            "/publish v1.2.3 " + "a" * 40,
        )
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(ValueError):
                MODULE.parse_release_command(value)

    def test_validator_path_is_optional_and_repository_relative_python(self):
        self.assertEqual(MODULE.validator_path(""), "")
        self.assertEqual(
            MODULE.validator_path("scripts/release/validate_release.py"),
            "scripts/release/validate_release.py",
        )
        for value in (
            "/tmp/validator.py",
            "../validator.py",
            "scripts/../validator.py",
            "scripts/release/validator.sh",
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                MODULE.validator_path(value)


if __name__ == "__main__":
    unittest.main()
