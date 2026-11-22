# Python library CI requirements

This document is the product contract for `tool.py.lib.ci`.

## 1. Scope

The tool provides generic CI for one ordinary Python library repository.

It is not a CAD CI system.

## 2. Repository input

The reusable workflow accepts at least:

- exact library source SHA;
- Python version, defaulting to Python 3.12;
- library test command or a documented default.

The test command supports `{python}` and `{repo}` placeholders. It is
executed directly without a shell.

The workflow always operates on the exact requested library commit.

## 3. Build

The workflow builds the library package as a wheel.

Requirements:

- build from the checked-out library source;
- produce exactly one `.whl`;
- fail if zero or multiple wheels are produced;
- do not import the library package from its source tree to prove success.

## 4. Clean installation

Create a clean Python environment for package verification.

Install:

1. the built wheel;
2. all dependencies declared by that wheel.

The test environment must not rely on dependencies that happen to exist in the
GitHub runner image.

During the test command, the clean environment's executable directory must be
first on `PATH` and `VIRTUAL_ENV` must point to that environment. Console
scripts installed by the wheel or its declared dependencies must therefore be
available to the tests.

## 5. Test execution

Run the library's complete declared test command in the clean environment.

The library repository controls test content.

The tool owns only execution and result propagation.

## 6. Failure classes

The workflow must clearly fail when:

- package build fails;
- wheel count is not exactly one;
- wheel/dependency installation fails;
- the library test command exits non-zero.

The public workflow does not reinterpret a failed test as success.

## 7. Source-isolation proof

The test environment must prove that the installed wheel is used rather than an
accidental import from the library working tree.

The initial implementation must include an automated test for this behavior.

## 8. Workflow consumption

The public GitHub Actions interface is one reusable workflow callable from
another repository.

Repositories pin one exact released repository revision.

## 9. No cache

The initial implementation uses no GitHub Actions cache.

There are no `actions/cache` restore/save steps and no private cache contract.

## 10. No CAD-CI/SCons

The tool must not invoke or depend on:

- `tool.cad.ci`;
- `lib.py.cad.ci`;
- SCons;
- `.cad-ci` state;
- `.cache/cad-ci`.

## 11. Evidence

The workflow logs must make these facts visible:

- checked-out library commit;
- Python version;
- built wheel filename;
- successful wheel installation;
- library test command;
- final pass/fail.

A separate durable build-store format is not required for the first release.

## 12. Release verification

Before a release is used by another repository:

1. repository tests pass;
2. the tool is released at an exact commit;
3. `tool.py.lib.ci.test` pins that exact release;
4. the external test repository passes.

## 13. Initial repository tests

The implementation repository must test at least:

- exact one-wheel detection;
- zero/multiple-wheel rejection;
- clean environment creation;
- wheel installation;
- dependency installation;
- passing test command;
- failing test command;
- build failure propagation;
- install failure propagation;
- source-tree import isolation;
- absence of SCons/CAD-CI/cache behavior.


## 14. Superseded run cancellation

The reusable workflow must cancel an older in-progress run when a newer run is
started for the same caller repository, caller workflow and PR/branch.

Different caller repositories, different caller workflows and different
PRs/branches must remain independent.

Consumer repositories must not need to duplicate this normal concurrency
policy.


## 15. Documentation-only pull requests

The reusable workflow may skip package build/install/test only for a pull
request when:

- no explicit `source_sha` override is supplied;
- at least one path changed;
- every changed path is below `docs/`.

The required workflow/job check must still complete successfully.

The workflow must print that full package validation was skipped because the
change is documentation-only.

All pushes, explicit source overrides, empty/unknown change sets, mixed changes
and changes outside `docs/` run the full package CI.


## 16. Documentation-only push events

In addition to the pull-request rule, the reusable workflow may classify a push
as documentation-only when all of these are true:

- the caller event is `push`;
- no explicit `source_sha` override is supplied;
- the push is not forced;
- the event provides a non-zero `before` commit;
- at least one path differs between `before` and the tested source commit;
- every changed path is below `docs/`.

Changed paths use a NUL-delimited Git diff with rename detection disabled.

Forced pushes, initial/zero-before pushes, malformed or unavailable context,
mixed changes and any path outside `docs/` must run full package CI.

### Change-scope output

The reusable workflow exposes one output named `change_scope`.

Its value is exactly:

- `docs-only`; or
- `full`.

The output reflects the scope used by the package-validation job. It lets a
caller avoid its own downstream release/publication job when that caller's
policy says documentation-only changes cannot produce a release.

The tool does not decide consumer release policy.


## 17. Reusable release publication

The tool exposes a second public GitHub Actions workflow for owner-issued
Python-library releases.

The workflow accepts:

- exact issue-comment command `/release vX.Y.Z <40-character-sha>`;
- triggering issue number;
- stable branch name, default `main`;
- optional repository-relative Python validator path.

Requirements:

- only an issue-comment release request is eligible;
- the triggering actor must equal the repository owner;
- input command/issue must match the triggering event;
- version is strict plain SemVer and SHA is exactly 40 lowercase hex;
- the exact called `tool.py.lib.ci` revision is used;
- the exact requested library source is checked out with refs/tags available;
- checkout credentials are not persisted;
- the requested target SHA must equal current configured stable-branch HEAD;
- a pre-existing tag on another commit fails closed;
- an existing matching tag/release is idempotent success;
- a missing release is created and the resulting tag is verified to resolve to
  the requested SHA;
- publication outputs include tag, target SHA and release URL;
- the workflow records the result on the triggering issue.

The release workflow owns generic GitHub tag/release transaction only. It does
not encode Forge/SolidCraft/CAD or package-specific release policy.

### Repository validator hook

When `validator_path` is set, the exact requested repository source is allowed
to execute one Python validator before publication.

The path must be safe, repository-relative and end in `.py`.

The validator is called with:

```text
--version X.Y.Z
--target-sha <sha>
--notes-out <temporary path>
```

A non-zero validator exit prevents publication. The validator may write release
notes to the provided path. It must not create Git tags/releases or own GitHub
publication.

## 18. Versioned consumer templates

The repository ships canonical wrappers for package CI and release publication.

Each template:

- has stable `template` id and positive integer `template-version`;
- is also listed in a machine-readable manifest;
- contains one explicit immutable release-SHA replacement marker;
- calls only a documented public reusable workflow;
- contains no copied generic checkout/build/test/tag/release implementation;
- contains no Forge/SolidCraft/CAD policy.

A new library repository starts from these templates and
`docs/new-library.md`, not from a locally invented generic workflow.
