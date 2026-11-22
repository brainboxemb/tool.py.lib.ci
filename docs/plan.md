# Repository plan

This file is the current source of truth for unfinished work in
`tool.py.lib.ci`.

## Released baseline

- `tool.py.lib.ci 0.2.0` @
  `8d18b3514180641e1756cc14efc4d8696c23e71b`;
- external live reusable-release acceptance run `45050396000` succeeded.

## Current work

### #19 — annotated generic release tags

Forge migration exposed one semantic gap: the generic publisher must create an
annotated release tag, not rely on the GitHub Release API to create a simple
tag ref.

Execution order:

1. create/verify annotated tag object + ref in the existing generic transaction;
2. reject pre-existing lightweight release tags;
3. preserve stable-head, exact-SHA, validator and idempotent release behavior;
4. release patch candidate `0.2.1` after repository CI is green;
5. externally publish `v0.2.1` in `tool.py.lib.ci.test` and verify Git ref
   type `tag`, exact target, validator notes and issue reporting;
6. then migrate Forge release.yml and delete its duplicate publisher.

## Open issue assessment — 2026-11-22

| Issue | Status | Assessment |
| --- | --- | --- |
| #19 Create annotated release tags in generic reusable release publication | **now** | Required before Forge migration; patch-only generic behavior correction. |
| #2 Implement Python library CI 0.1.0 core | **later / historical cleanup** | Released behavior already exists; does not block #19. |

## Boundary

No workflow/template topology change is required for #19. The released
`tool.py.lib.ci/release` template remains version 1.
