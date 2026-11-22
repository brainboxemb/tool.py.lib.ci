from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "publish_release.py"
SPEC = spec_from_file_location("publish_release", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"could not load {SCRIPT}")
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

SHA_A = "a" * 40
SHA_B = "b" * 40
SHA_C = "c" * 40


def not_found() -> HTTPError:
    return HTTPError("https://api.github.com", 404, "Not found", {}, None)


class ReleaseTests(unittest.TestCase):
    def test_release_version_requires_matching_changelog_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "VERSION").write_text("0.1.0\n", encoding="utf-8")
            (root / "CHANGELOG.md").write_text(
                "# Changelog\n\n## 0.1.0\n",
                encoding="utf-8",
            )
            self.assertEqual(MODULE.release_version(root), "0.1.0")

    def test_invalid_version_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "VERSION").write_text("dev\n", encoding="utf-8")
            (root / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                MODULE.release_version(root)

    def test_create_annotated_tag_creates_tag_object_then_ref(self):
        base = "https://api.github.com/repos/owner/repo"
        with patch.object(MODULE, "_request", side_effect=[
            {"sha": SHA_C},
            {},
        ]) as request:
            MODULE._create_annotated_tag(
                base,
                "v1.2.3",
                SHA_A,
                "token",
            )

        create_tag = request.call_args_list[0]
        self.assertEqual(create_tag.args[0], f"{base}/git/tags")
        self.assertEqual(create_tag.kwargs["method"], "POST")
        self.assertEqual(
            create_tag.kwargs["data"],
            {
                "tag": "v1.2.3",
                "message": "v1.2.3",
                "object": SHA_A,
                "type": "commit",
            },
        )

        create_ref = request.call_args_list[1]
        self.assertEqual(create_ref.args[0], f"{base}/git/refs")
        self.assertEqual(create_ref.kwargs["method"], "POST")
        self.assertEqual(
            create_ref.kwargs["data"],
            {"ref": "refs/tags/v1.2.3", "sha": SHA_C},
        )

    def test_existing_exact_annotated_release_is_idempotent(self):
        annotated = {"type": "tag", "sha": SHA_C}
        with (
            patch.object(MODULE, "_tag_reference", return_value=annotated),
            patch.object(MODULE, "_tag_commit", return_value=SHA_A),
            patch.object(MODULE, "_request", side_effect=[
                {"object": {"type": "commit", "sha": SHA_A}},  # main
                {"html_url": "https://example.test/releases/v1.2.3"},
            ]) as request,
        ):
            result = MODULE.publish_exact_release(
                "owner/repo", "1.2.3", SHA_A, "token"
            )
        self.assertFalse(result.created)
        self.assertEqual(result.tag, "v1.2.3")
        self.assertEqual(result.target_sha, SHA_A)
        self.assertEqual(request.call_count, 2)

    def test_existing_lightweight_tag_is_rejected(self):
        lightweight = {"type": "commit", "sha": SHA_A}
        with (
            patch.object(MODULE, "_tag_reference", return_value=lightweight),
            patch.object(MODULE, "_request", return_value={
                "object": {"type": "commit", "sha": SHA_A},
            }),
        ):
            with self.assertRaisesRegex(ValueError, "not an annotated tag"):
                MODULE.publish_exact_release(
                    "owner/repo", "1.2.3", SHA_A, "token"
                )

    def test_existing_annotated_tag_on_other_commit_fails_closed(self):
        annotated = {"type": "tag", "sha": SHA_C}
        with (
            patch.object(MODULE, "_tag_reference", return_value=annotated),
            patch.object(MODULE, "_tag_commit", return_value=SHA_B),
            patch.object(MODULE, "_request", return_value={
                "object": {"type": "commit", "sha": SHA_A},
            }),
        ):
            with self.assertRaisesRegex(ValueError, "refusing to relabel"):
                MODULE.publish_exact_release(
                    "owner/repo", "1.2.3", SHA_A, "token"
                )

    def test_release_target_must_equal_stable_head(self):
        with patch.object(MODULE, "_request", return_value={
            "object": {"type": "commit", "sha": SHA_B},
        }):
            with self.assertRaisesRegex(ValueError, "must equal main HEAD"):
                MODULE.publish_exact_release(
                    "owner/repo", "1.2.3", SHA_A, "token"
                )

    def test_missing_release_creates_annotated_tag_then_release(self):
        annotated = {"type": "tag", "sha": SHA_C}
        with (
            patch.object(
                MODULE,
                "_tag_reference",
                side_effect=[None, annotated],
            ),
            patch.object(MODULE, "_tag_commit", return_value=SHA_A),
            patch.object(MODULE, "_create_annotated_tag") as create_tag,
            patch.object(MODULE, "_request", side_effect=[
                {"object": {"type": "commit", "sha": SHA_A}},  # main
                not_found(),  # release missing
                {"html_url": "https://example.test/releases/v1.2.3"},
            ]) as request,
        ):
            result = MODULE.publish_exact_release(
                "owner/repo",
                "1.2.3",
                SHA_A,
                "token",
                notes="qualified notes\n",
            )

        self.assertTrue(result.created)
        create_tag.assert_called_once_with(
            "https://api.github.com/repos/owner/repo",
            "v1.2.3",
            SHA_A,
            "token",
        )
        post = request.call_args_list[2]
        self.assertEqual(post.kwargs["method"], "POST")
        self.assertEqual(post.kwargs["data"]["tag_name"], "v1.2.3")
        self.assertNotIn("target_commitish", post.kwargs["data"])
        self.assertEqual(post.kwargs["data"]["body"], "qualified notes\n")

    def test_missing_notes_uses_github_generated_release_notes(self):
        annotated = {"type": "tag", "sha": SHA_C}
        with (
            patch.object(
                MODULE,
                "_tag_reference",
                side_effect=[None, annotated],
            ),
            patch.object(MODULE, "_tag_commit", return_value=SHA_A),
            patch.object(MODULE, "_create_annotated_tag"),
            patch.object(MODULE, "_request", side_effect=[
                {"object": {"type": "commit", "sha": SHA_A}},
                not_found(),
                {"html_url": "https://example.test/releases/v1.2.3"},
            ]) as request,
        ):
            MODULE.publish_exact_release("owner/repo", "1.2.3", SHA_A, "token")
        self.assertTrue(
            request.call_args_list[2].kwargs["data"]["generate_release_notes"]
        )

    def test_annotated_tag_resolves_to_exact_commit(self):
        with patch.object(MODULE, "_request", side_effect=[
            {"object": {"type": "tag", "sha": SHA_C}},
            {"object": {"type": "commit", "sha": SHA_A}},
        ]):
            self.assertEqual(
                MODULE._tag_commit(
                    "https://api.github.com/repos/owner/repo",
                    "v1.2.3",
                    "token",
                ),
                SHA_A,
            )


if __name__ == "__main__":
    unittest.main()
