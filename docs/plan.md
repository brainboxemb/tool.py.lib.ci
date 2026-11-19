# Repository plan

This file is the current source of truth for unfinished work in
`tool.py.lib.ci`.

Requirements live in `docs/requirements.md`. Architecture lives in
`docs/design.md`.

## Current status

The latest released and externally tested revision is:

- version: 0.1.2
- commit: `9045367540102ba2208c517e45a52ddad4bb60ea`

The tool now builds one wheel, installs it with dependencies in a clean
environment, runs tests outside the source tree, and exposes installed console
scripts through the clean environment PATH.

There is no active functional implementation work in this repository at this
snapshot. Current work is in library repositories adopting the released tool.

## Open issue assessment — 2026-11-19

| Issue | Status | Assessment |
| --- | --- | --- |
| #8 Make docs/plan.md the repository work source of truth | now | Repository-process housekeeping. Close after this plan/AGENTS update is merged. |
| #2 Implement Python library CI 0.1.0 core | effectively complete but still open | The core was implemented and released as 0.1.0, then refined through 0.1.2 and externally tested. Review the original checklist and close if no historical requirement remains. |

## Next action

Do not invent new tool work while `lib.py.cad.ci` and
`lib.py.cad.verfication` adopt 0.1.2. If those migrations expose a genuinely
generic Python-library CI defect, open a new focused issue here, fix it, release
a new exact revision, and test that revision externally before adoption.
