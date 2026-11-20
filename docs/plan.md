# Repository plan

This file is the current source of truth for unfinished work in
`tool.py.lib.ci`.

Requirements live in `docs/requirements.md`. Architecture lives in
`docs/design.md`.

## Current status

The latest released and externally tested revision is:

- version: 0.1.2
- commit: `9045367540102ba2208c517e45a52ddad4bb60ea`

The tool builds one wheel, installs it with dependencies in a clean
environment, runs tests outside the source tree, and exposes installed console
scripts through the clean environment PATH.

## Current goal

Complete #10: cancel superseded reusable Python-library CI runs centrally.

This must remain generic Python-library CI behavior. Consumer repositories must
not need their own concurrency block for normal library CI.

## Execution order

1. Add one reusable-workflow concurrency contract that separates caller
   repository, caller workflow and PR/branch.
2. Set `cancel-in-progress: true` so a newer run supersedes only an older run
   for that same caller scope.
3. Prove the public workflow contract in repository tests.
4. Release the change only after repository CI is green.
5. Update `tool.py.lib.ci.test` to the exact release and externally prove it.
6. Then implement #11 as a separate change.

## Open issue assessment — 2026-11-20

| Issue | Status | Assessment |
| --- | --- | --- |
| #10 Cancel superseded Python library CI runs centrally | now | Small generic maintenance improvement that prevents wasted overlapping library CI work. |
| #11 Skip expensive Python-library tests for documentation-only changes | next | Larger maintenance optimization; keep separate from concurrency cancellation. |
| #2 Implement Python library CI 0.1.0 core | effectively complete but still open | Core behavior shipped through 0.1.2 and is externally tested; close separately after historical checklist review. |

## Boundary

No CAD-CI, SCons, Forge, model-selection or cache behavior belongs in this
repository.
