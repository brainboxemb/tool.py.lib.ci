"""Contract tests for the public reusable release workflow."""

from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "reusable-release.yml"


def load_yaml(path: Path) -> dict:
    value = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    if not isinstance(value, dict):
        raise AssertionError(f"{path}: expected mapping")
    return value


class ReusableReleaseWorkflowTests(unittest.TestCase):
    def test_public_inputs_outputs_and_permissions(self):
        wf = load_yaml(WORKFLOW)
        call = wf["on"]["workflow_call"]
        self.assertEqual(
            set(call["inputs"]),
            {"command", "issue_number", "stable_ref", "validator_path"},
        )
        self.assertEqual(
            set(call["outputs"]),
            {"tag", "target_sha", "release_url"},
        )
        self.assertEqual(wf["permissions"]["contents"], "read")
        job = wf["jobs"]["release"]
        self.assertEqual(job["permissions"]["contents"], "write")
        self.assertEqual(job["permissions"]["issues"], "write")
        self.assertEqual(job["concurrency"]["cancel-in-progress"], "false")
        self.assertIn("github.repository", job["concurrency"]["group"])
        self.assertEqual(job["timeout-minutes"], "10")

    def test_context_validation_precedes_any_consumer_code(self):
        wf = load_yaml(WORKFLOW)
        steps = wf["jobs"]["release"]["steps"]
        self.assertEqual(steps[0]["name"], "Validate caller release context")
        self.assertIn("repository owner", steps[0]["run"])
        tool_checkout = next(
            i for i, step in enumerate(steps)
            if step.get("name") == "Checkout called release tool revision"
        )
        source_checkout = next(
            i for i, step in enumerate(steps)
            if step.get("name") == "Checkout exact requested library source"
        )
        validator = next(
            i for i, step in enumerate(steps)
            if step.get("name") == "Run repository release validator"
        )
        publish = next(
            i for i, step in enumerate(steps)
            if step.get("name") == "Publish or verify exact GitHub release"
        )
        self.assertLess(0, tool_checkout)
        self.assertLess(tool_checkout, source_checkout)
        self.assertLess(source_checkout, validator)
        self.assertLess(validator, publish)

    def test_tool_and_source_checkouts_are_exact_and_do_not_persist_credentials(self):
        wf = load_yaml(WORKFLOW)
        steps = wf["jobs"]["release"]["steps"]
        tool = next(
            step for step in steps
            if step.get("name") == "Checkout called release tool revision"
        )
        source = next(
            step for step in steps
            if step.get("name") == "Checkout exact requested library source"
        )
        self.assertEqual(tool["with"]["repository"], "${{ job.workflow_repository }}")
        self.assertEqual(tool["with"]["ref"], "${{ job.workflow_sha }}")
        self.assertEqual(tool["with"]["persist-credentials"], "false")
        self.assertEqual(source["with"]["ref"], "${{ steps.request.outputs.target_sha }}")
        self.assertEqual(source["with"]["fetch-depth"], "0")
        self.assertEqual(source["with"]["fetch-tags"], "true")
        self.assertEqual(source["with"]["persist-credentials"], "false")

    def test_validator_hook_is_constrained_and_publication_uses_tool_script(self):
        wf = load_yaml(WORKFLOW)
        steps = wf["jobs"]["release"]["steps"]
        validator = next(
            step for step in steps
            if step.get("name") == "Run repository release validator"
        )
        self.assertIn("--version", validator["run"])
        self.assertIn("--target-sha", validator["run"])
        self.assertIn("--notes-out", validator["run"])
        self.assertNotIn("gh api", validator["run"])

        publish = next(
            step for step in steps
            if step.get("name") == "Publish or verify exact GitHub release"
        )
        self.assertIn("scripts/release_command.py", publish["run"])
        self.assertIn(" publish ", publish["run"])
        self.assertIn("--stable-ref", publish["run"])

        report = next(
            step for step in steps
            if step.get("name") == "Record release on triggering issue"
        )
        self.assertIn("gh api -X POST", report["run"])


if __name__ == "__main__":
    unittest.main()
