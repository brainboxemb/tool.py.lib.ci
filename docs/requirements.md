# Python library CI requirements

This document is the product contract for `tool.py.lib.ci`.

## 1. Scope

The tool provides generic CI for one ordinary Python library repository.

It is not a CAD CI system.

## 2. Consumer input

The reusable workflow accepts at least:

- exact consumer source SHA;
- Python version, defaulting to Python 3.12;
- consumer test command or a documented default.

The workflow always operates on the exact requested consumer commit.

## 3. Build

The workflow builds the consumer package as a wheel.

Requirements:

- build from the checked-out consumer source;
- produce exactly one `.whl`;
- fail if zero or multiple wheels are produced;
- do not import the consumer package from its source tree to prove success.

## 4. Clean installation

Create a clean Python environment for package verification.

Install:

1. the built wheel;
2. all dependencies declared by that wheel.

The test environment must not rely on dependencies that happen to exist in the
GitHub runner image.

## 5. Test execution

Run the consumer's complete declared test command in the clean environment.

The consumer controls test content.

The tool owns only execution and result propagation.

## 6. Failure classes

The workflow must clearly fail when:

- package build fails;
- wheel count is not exactly one;
- wheel/dependency installation fails;
- the consumer test command exits non-zero.

The public workflow does not reinterpret a failed test as success.

## 7. Source-isolation proof

The test environment must prove that the installed wheel is used rather than an
accidental import from the consumer working tree.

The initial implementation must include an automated test for this behavior.

## 8. Workflow consumption

The public GitHub Actions interface is one reusable workflow callable from
another repository.

Consumers pin one exact released repository revision.

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

- checked-out consumer commit;
- Python version;
- built wheel filename;
- successful wheel installation;
- consumer test command;
- final pass/fail.

A separate durable build-store format is not required for the first release.

## 12. Release qualification

Before a release is adopted by consumers:

1. repository tests pass;
2. the tool is released at an exact commit;
3. `tool.py.lib.ci.test` pins that exact release;
4. black-box acceptance passes from the external test repository.

## 13. Initial acceptance tests

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
