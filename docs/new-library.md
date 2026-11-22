# Set up a new Python library repository

Use the released `tool.py.lib.ci` workflows instead of building package CI or
release publication locally.

## 1. Copy the CI template

Copy `templates/github/workflows/ci.yml` to the new repository and replace
`TOOL_PY_LIB_CI_RELEASE_SHA` with one exact released and externally accepted
commit.

The reusable CI workflow builds exactly one wheel, installs it in a clean
environment and runs the repository test command against the installed package.

## 2. Copy the release template

Copy `templates/github/workflows/release.yml` and pin the same exact released
tool commit.

An owner publishes with:

```text
/release vX.Y.Z <40-character-main-sha>
```

The reusable release workflow:

1. verifies the issue-comment context and repository owner;
2. parses exact SemVer and SHA;
3. checks out the exact requested library commit with full refs/tags available;
4. optionally runs the repository release validator;
5. requires the target SHA to equal the configured stable branch head;
6. creates or verifies the exact tag and GitHub Release;
7. records the release URL on the triggering issue.

## 3. Optional repository validator

Generic publication does not know repository/domain release policy. A
repository that needs extra qualification adds:

```yaml
with:
  validator_path: scripts/release/validate_release.py
```

The validator is checked out from the exact requested release commit and is
called as:

```text
python <validator> \
  --version X.Y.Z \
  --target-sha <sha> \
  --notes-out <temporary-markdown-file>
```

It must be self-contained for the runner's Python environment. It may validate
package metadata, changelog, durable evidence or other repository-owned rules.
If it writes release notes, those notes become the GitHub Release body.
Without notes, GitHub-generated release notes are used.

The validator does **not** create tags/releases or call GitHub APIs.

## 4. Keep template provenance

Do not remove:

```yaml
# template: tool.py.lib.ci/<id>
# template-version: 1
```

Current template ids/versions are recorded in
`templates/manifest.json`. Change the copied wrapper only for documented
repository-owned values. Generic package build/test/release behavior belongs
back in `tool.py.lib.ci`.

## 5. Release adoption order

A new `tool.py.lib.ci` version is:

1. tested in this repository;
2. released at an exact commit;
3. pinned by `tool.py.lib.ci.test`;
4. externally accepted there;
5. only then adopted by real library repositories.
