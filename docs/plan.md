# Repository plan

This file is the current source of truth for unfinished work in
`tool.py.lib.ci`.

Requirements live in `docs/requirements.md`. Architecture lives in
`docs/design.md`.

## Released baseline

The latest released revision is:

- version: 0.1.5
- commit: `d189d0718659ca3927f1dddbe373c1c788b11b6c`

Issue #14 is complete in 0.1.5: safely comparable documentation-only push
events expose `change_scope` and can avoid package validation.

## Current goal

### #17 — reusable Python-library release workflow

Move generic release transaction/orchestration out of real library consumers.

Execution order:

1. expose `reusable-release.yml` as a public owner-issued exact-SHA release
   workflow;
2. reuse one generic tag/GitHub Release transaction in
   `scripts/publish_release.py`;
3. provide a constrained repository validator hook for domain/package policy;
4. ship versioned CI/release consumer templates plus new-library onboarding;
5. cover command parsing, stable-head/tag idempotency, validator ordering,
   permissions and template contracts in repository tests;
6. release candidate is `0.2.0`; release only after repository CI is green;
7. update `tool.py.lib.ci.test` to the exact release and externally prove the
   public release workflow;
8. only then replace Forge's locally invented generic release workflow with the
   released canonical template while retaining Forge-specific validation.

## Open issue assessment — 2026-11-22

| Issue | Status | Assessment |
| --- | --- | --- |
| #17 Expose reusable Python-library release workflow with versioned consumer template | **now** | Current product work; must be released/externally accepted before Forge migration. |
| #2 Implement Python library CI 0.1.0 core | **later / historical cleanup** | Core behavior is already released; review/close historical checklist separately without blocking #17. |

## Boundary

This tool owns generic Python package CI and generic GitHub release
publication. A consumer owns its package/domain release qualification through
the validator hook.

No CAD-CI, SCons, Forge/SolidCraft/model policy or durable CAD publication
algorithm belongs here.
