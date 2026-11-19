# tool.py.lib.ci

Generic CI for ordinary Python libraries.

The tool provides one reusable GitHub Actions workflow that builds and tests a
consumer Python package from the outside.

## Purpose

A Python library should not need CAD-CI, SCons or repository-specific workflow
logic merely to prove that its released package can be built and tested.

`tool.py.lib.ci` owns that generic package-CI path.

Typical consumers include reusable Python libraries such as
`lib.py.cad.verfication`.

## Responsibilities

The first release must:

- check out the exact consumer source commit;
- set up the requested Python version;
- build exactly one wheel;
- create a clean test environment;
- install that wheel including declared dependencies;
- run the consumer test command against the installed wheel;
- fail clearly on build, install or test failure;
- expose a simple successful/failed workflow result.

## Hard boundaries

This tool does **not** provide:

- SCons;
- CAD-CI items or model selection;
- changed-model dependency graphs;
- CAD build branches;
- Pages publication;
- Forge/SolidCraft/CAD policy;
- GitHub Actions cache in the initial implementation.

`tool.cad.ci` remains the generic CI layer for Forge/CAD repositories.

## Released-stack rule

A consumer must pin an exact released `tool.py.lib.ci` revision.

Before a consumer adopts a release, that exact revision must pass the
black-box acceptance repository:

`brainboxemb/tool.py.lib.ci.test`

## Documentation

- `docs/requirements.md` — observable tool contract.
- `docs/design.md` — implementation architecture.
- `docs/plan.md` — current unfinished repository work only.
