# Repository plan

This file is the current source of truth for unfinished work in
`tool.py.lib.ci`.

Requirements live in `docs/requirements.md`. Architecture lives in
`docs/design.md`.

## Current status

Release 0.1.1 exists at exact commit
`414db795c757af5c4f9eaff7f6fd65f27870d7d1`.

The initial build-one-wheel, clean-install and test path is therefore already
implemented and released. Do not redo the 0.1.0/0.1.1 core.

## Current work

### 1. Expose installed wheel command scripts during library tests — #5

PR #7 is the active tool change.

Finish and release it only if the external/library migrations require installed
console-script commands to be available in the clean test environment.

### 2. External test of the released tool

`tool.py.lib.ci.test#3` must pin an exact released tool revision and pass from
another repository before that revision is adopted by Python library
repositories.

### 3. Library migrations

After external test passes:

1. migrate `lib.py.cad.ci` own repository CI;
2. migrate `lib.py.cad.verfication` own repository CI.

Those migrations are tracked in their own repositories and must not add
CAD-specific behavior here.

## Open issue assessment — 2026-11-19

| Issue | Status | Assessment |
| --- | --- | --- |
| #5 Expose installed wheel command scripts during library tests | now | Active PR #7. Required if library tests invoke installed command entry points; keep the behavior generic. |
| #2 Implement Python library CI 0.1.0 core | effectively complete but still open | Core functionality was released as 0.1.0 and then 0.1.1. Review the original checklist, close if fully satisfied, and do not treat it as new implementation work. |

Do not add SCons, CAD-CI, Pages, model selection or GitHub Actions cache here.
