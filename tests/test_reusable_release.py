"""Contract tests for the public reusable release workflow."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "reusable-release.yml"


class ReusableReleaseWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_public_inputs_outputs_and_permission_boundary(self):
        for value in (
            "workflow_call:",
            "command:",
            "issue_number:",
            "stable_ref:",
            "validator_path:",
            "tag:",
            "target_sha:",
            "release_url:",
            "contents: read",
            "contents: write",
            "issues: write",
            "timeout-minutes: 10",
            "cancel-in-progress: false",
            "py-lib-release-${{ github.repository }}",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.workflow)

    def test_context_validation_precedes_any_consumer_code(self):
        names = (
            "Validate caller release context",
            "Checkout called release tool revision",
            "Parse exact release request",
            "Checkout exact requested library source",
            "Run repository release validator",
            "Publish or verify exact GitHub release",
            "Record release on triggering issue",
        )
        positions = [self.workflow.index(name) for name in names]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("only the repository owner may publish", self.workflow)
        self.assertIn("issue_number does not match triggering issue", self.workflow)
        self.assertIn("command does not match triggering comment", self.workflow)

    def test_checkouts_are_exact_and_do_not_persist_credentials(self):
        self.assertIn("repository: ${{ job.workflow_repository }}", self.workflow)
        self.assertIn("ref: ${{ job.workflow_sha }}", self.workflow)
        self.assertIn("ref: ${{ steps.request.outputs.target_sha }}", self.workflow)
        self.assertIn("fetch-depth: 0", self.workflow)
        self.assertIn("fetch-tags: true", self.workflow)
        self.assertGreaterEqual(self.workflow.count("persist-credentials: false"), 2)

    def test_validator_and_publication_contract(self):
        validator = self.workflow[
            self.workflow.index("Run repository release validator"):
            self.workflow.index("Publish or verify exact GitHub release")
        ]
        self.assertIn("--version", validator)
        self.assertIn("--target-sha", validator)
        self.assertIn("--notes-out", validator)
        self.assertNotIn("gh api", validator)

        publish = self.workflow[
            self.workflow.index("Publish or verify exact GitHub release"):
            self.workflow.index("Record release on triggering issue")
        ]
        self.assertIn("scripts/release_command.py", publish)
        self.assertIn(" publish ", publish)
        self.assertIn("--stable-ref", publish)
        self.assertIn("--notes-file", publish)

        report = self.workflow[self.workflow.index("Record release on triggering issue"):]
        self.assertIn("gh api -X POST", report)


if __name__ == "__main__":
    unittest.main()
