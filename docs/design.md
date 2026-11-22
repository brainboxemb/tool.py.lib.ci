# Python library CI design

This document describes the implementation architecture for the requirements in
`docs/requirements.md`.

## 1. Public surfaces

The released public workflows are:

```text
.github/workflows/reusable-ci.yml
.github/workflows/reusable-release.yml
```

Repositories call those workflows at one exact released commit. Canonical
consumer wrappers live in `templates/github/workflows/`.

## 2. Thin workflow

The workflow owns only GitHub-hosted setup:

1. checkout the library repository at the exact source SHA;
2. setup the requested Python version;
3. call the repository's package-CI script.

Build/test semantics live in a normal script so they can also be tested locally.

## 3. Package-CI script

Use one small Python script, for example:

```text
scripts/library_ci.py
```

It owns:

- wheel build;
- exactly-one-wheel validation;
- clean virtual environment creation;
- wheel/dependency installation;
- library test command execution;
- concise terminal output.

It does not own repository selection, caching or release publication.

## 4. Wheel build

The script builds into a temporary/output directory using standard Python
packaging tooling.

The result is valid only when exactly one wheel exists.

## 5. Clean test environment

Create a new `venv`.

Install the wheel with normal dependency resolution.

Run tests from a working directory that cannot accidentally expose the library
package source as an import location.

For the test process:
- prepend the clean environment's `bin` / `Scripts` directory to `PATH`;
- set `VIRTUAL_ENV` to the clean environment;
- preserve the remaining process environment.

This makes installed console scripts available without adding the source tree to
Python's import path.

## 6. Library test command

The workflow passes the documented library test command to the script.

The command is parsed without a shell and supports:

- `{python}`: clean-environment Python executable;
- `{repo}`: absolute library repository root.

The empty/default command is:

```text
{python} -m unittest discover -s {repo}/tests -p test_*.py -v
```

Repositories may override it. Do not embed pytest or unittest policy beyond that
explicit interface.

## 7. No cache/state engine

There is no SCons graph and no GitHub Actions cache.

Every workflow run is intentionally a clean package build/test.

## 8. Release

Release plumbing belongs to this repository, but release publication runs only
after the repository's own tests pass on `main`.

The released repository commit is the public pin used by repositories and by
`tool.py.lib.ci.test`.

## 9. External test repository

`tool.py.lib.ci.test` calls the released reusable workflow from another
repository.

That repository proves the public GitHub Actions contract. It must not
reimplement generic package-CI behavior.


## 10. Reusable workflow concurrency

The reusable workflow owns one GitHub Actions concurrency group.

The group key is derived from caller context and must distinguish:

- caller repository;
- caller workflow;
- caller PR/branch reference.

`cancel-in-progress` is enabled.

This is workflow scheduling only. It does not introduce cache, incremental
execution or repository-selection behavior.


## 11. Documentation-only classification

The called workflow still checks out the caller source and the exact called
tool revision.

For a normal pull request with no explicit `source_sha`, it fetches the exact
PR base commit and obtains a NUL-delimited changed-path list with Git rename
detection disabled. Disabling rename detection makes a code-to-docs move appear
as a code deletion plus docs addition, so it cannot be misclassified as
documentation-only.

A small tool-owned classifier returns `docs-only` only for a non-empty set in
which every path starts with `docs/`.

The workflow then:

- emits one explicit docs-only skip message and returns success; or
- sets up Python and runs the unchanged package-CI script.

Unknown input always selects the full path.


## 12. Push classification and workflow output

The change-classification step selects one comparison range:

- pull request: `pull_request.base.sha .. tested source sha`;
- normal push: `event.before .. tested source sha`;
- all other contexts: no comparison, therefore `full`.

Before using the push range, the workflow checks that:

- `source_sha` input is empty;
- the push is not forced;
- `before` is a 40-character hexadecimal SHA that is not all zeroes.

The selected base commit is fetched explicitly. Git then produces
NUL-delimited names with rename detection disabled.

The `test` job exports the classifier result as `change_scope`, and
`workflow_call.outputs.change_scope` forwards that exact job output to the
caller.

This output is observation only. It does not create package-release policy in
the tool.


## 13. Reusable release architecture

The release workflow is deliberately separate from package CI and from
repository-specific release qualification.

```text
issue comment /release vX.Y.Z <sha>
  -> validate caller/event ownership
  -> checkout exact called tool revision
  -> parse command with scripts/release_command.py
  -> checkout exact consumer SHA with full refs/tags
  -> optional consumer validator
  -> scripts/release_command.py publish
       -> generic publish_exact_release()
       -> stable HEAD check
       -> annotated tag object/ref check or creation
       -> GitHub Release create or idempotent verify
       -> verify final tag resolves to exact SHA
  -> comment release URL on triggering issue
```

The generic GitHub transaction lives in `scripts/publish_release.py` and is
also reused by this tool's own release script path. There is one tag/release
implementation, not a consumer copy.

The consumer validator is the policy extension point. It runs from the exact
requested source checkout and receives only version, target SHA and notes path
as its public argument contract. The workflow does not know package layout,
changelog format, durable evidence or domain release blockers.

The source checkout uses full refs/tags because a repository validator may
validate durable/generated refs. Credentials are not persisted. The validator
runs before `GITHUB_TOKEN` is passed to the publication script.

## 14. Consumer template architecture

`templates/manifest.json` records canonical template id, integer version and
public workflow surface.

The copied wrappers contain triggers, permissions and repository-owned inputs
only. They never contain package build/test or GitHub tag/release
implementation.

Template-version increments when the copied wrapper contract changes. Tool
semantic version and template version remain separate concepts.


### Annotated tag contract

A missing release tag is created explicitly through the Git Data API:

```text
POST git/tags   -> annotated tag object pointing to target commit
POST git/refs   -> refs/tags/vX.Y.Z points to that tag object
verify          -> tag object resolves to exact target commit
POST releases   -> release references the already-existing tag
```

A lightweight pre-existing release tag is rejected. This keeps the generic
publisher compatible with libraries whose immutable release contract requires
annotated tags.
