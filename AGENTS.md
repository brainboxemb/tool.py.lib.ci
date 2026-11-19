# Repository instructions

## Purpose

`tool.py.lib.ci` is the generic CI tool for ordinary Python libraries.

It proves the released-package shape of a consumer from outside that consumer's
source package.

## Hard boundary

Do not add CAD-CI behavior here.

Specifically, do not add:

- SCons;
- CAD item selection;
- CAD dependency graphs;
- Forge/SolidCraft/model policy;
- CAD build or Pages publication.

If a feature is specific to CAD repositories, it belongs in `tool.cad.ci`.

## Cache rule

Do not add GitHub Actions cache to the initial implementation.

Only add caching later when a measured need and an explicit requirement justify
it.

## Development process

Before changing behavior:

1. update `docs/requirements.md`;
2. update `docs/design.md` when architecture changes;
3. add tests;
4. implement the smallest change satisfying the contract;
5. release only after repository tests pass;
6. update `tool.py.lib.ci.test` to pin that exact release;
7. only after black-box acceptance passes may consumers update their pin.

## Repository plan

Current unfinished work lives in `docs/plan.md`.

The plan contains only unfinished work. Remove completed sections after merge
and release. Permanent behavior belongs in requirements/design; issues preserve
detail and history.

## Change quality

Use short literal engineering language.

Non-obvious scripts need explanatory docstrings/comments.

Keep one logical change per branch/PR and prefer squash merges.
