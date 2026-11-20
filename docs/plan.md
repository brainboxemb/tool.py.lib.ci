# Repository plan

This file is the current source of truth for unfinished work in
`tool.py.lib.ci`.

Requirements live in `docs/requirements.md`. Architecture lives in
`docs/design.md`.

## Current status

The latest released revision is:

- version: 0.1.3
- commit: `801480ad10b31d417ed7843f44608c795032c6d5`

It adds central superseded-run cancellation. The exact release has passed the
external `tool.py.lib.ci.test` PR acceptance.

## Current goal

Complete #11: keep the required reusable CI check successful for documentation-
only pull requests while skipping the expensive package build/install/test path.

## Docs-only rule

The cheap path is allowed only when all of these are true:

- the caller event is `pull_request`;
- `source_sha` was not explicitly overridden;
- at least one file changed;
- every changed path is below `docs/`.

Everything else runs the full package CI.

## Execution order

1. Add one small, directly tested path classifier.
2. In the reusable workflow, fetch the PR base and classify changed paths with
   rename detection disabled.
3. For docs-only changes:
   - keep the same successful workflow/job check;
   - skip setup-python and package build/install/test;
   - print a literal skip reason.
4. For all other cases, preserve the existing full CI path unchanged.
5. Release only after repository CI is green.
6. Externally test the exact release in `tool.py.lib.ci.test`.
7. Prove the actual cheap path in a library consumer before closing its
   corresponding consumer issue.

## Open issue assessment — 2026-11-20

| Issue | Status | Assessment |
| --- | --- | --- |
| #11 Skip expensive Python-library tests for documentation-only changes | now | Current maintenance optimization; conservative docs-only rule preserves one required check. |
| #2 Implement Python library CI 0.1.0 core | effectively complete but still open | Core behavior shipped and remains covered; close separately after historical checklist review. |

## Boundary

No CAD-CI, SCons, Forge, model-selection or cache behavior belongs here.
