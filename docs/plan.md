# Repository plan

This file is the current source of truth for unfinished work in
`tool.py.lib.ci`.

Requirements live in `docs/requirements.md`. Architecture lives in
`docs/design.md`.

## Current status

The latest released and externally accepted revision is:

- version: 0.1.4
- commit: `81461fa4b61c90b91b0427ce3e99a493c2dc2e78`

Version 0.1.4 makes documentation-only pull requests cheap, but a squash merge
of that same change still runs the full package path on the resulting `push`.

Measured in `lib.py.cad.ci`:

- docs-only pull-request test job: about 6-7 seconds;
- post-merge main test job: about 35 seconds;
- post-merge release job: about 12 seconds.

## Current goal

Complete #14: safely classify documentation-only push events and expose the
selected change scope to callers.

## Execution order

1. Extend change-scope selection to normal non-forced push events using the
   event `before` commit and tested source commit.
2. Fail safe to full CI for forced pushes, zero/unknown before SHAs, explicit
   source overrides and any mixed/non-doc change.
3. Keep NUL-delimited paths and `--no-renames`.
4. Expose `change_scope` as a reusable-workflow output with values
   `docs-only` or `full`.
5. Preserve existing pull-request semantics.
6. Release only after repository tests pass.
7. Update `tool.py.lib.ci.test` to the exact release and externally prove the
   push/output contract.
8. Update a real consumer to the exact release and use
   `needs.<job>.outputs.change_scope` to skip its release job for docs-only
   main pushes.
9. Prove the complete docs-only PR + main path in the consumer.

## Open issue assessment — 2026-11-20

| Issue | Status | Assessment |
| --- | --- | --- |
| #14 Skip package CI for safely classified documentation-only pushes | now | Current maintenance optimization; removes the remaining full main test and enables release-job suppression. |
| #2 Implement Python library CI 0.1.0 core | effectively complete but still open | Core behavior shipped through multiple accepted releases; close separately after historical checklist review. |

## Boundary

No CAD-CI, SCons, Forge, model-selection or package-release policy belongs here.
The tool exposes generic change scope; each consumer decides what its own
release job does with that output.
