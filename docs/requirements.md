# Python library CI requirements

This document is the product contract for `tool.py.lib.ci`.

## 1. Scope

The tool provides generic CI for one ordinary Python library repository.

It is not a CAD CI system.

## 2. Repository input

The reusable workflow accepts at least:

- exact library source SHA;
- Python version, defaulting to Python 3.12;
- library test command or a documented default.

The test command supports `{python}` and `{repo}` placeholders. It is
executed directly without a shell.

The workflow always operates on the exact requested library commit.

## 3. Build

The workflow builds the library package as a wheel.

Requirements:

- build from the checked-out library source;
- produce exactly one `.whl`;
- fail if zero or multiple wheels are produced;
- do not import the library package from its source tree to prove success.

## 4. Clean installation

Create a clean Python environment for package verification.

Install:

1. the built wheel;
2. all dependencies declared by that wheel.

The test environment must not rely on dependencies that happen to exist in the
GitHub runner image.

During the test command, the clean environment's executable directory must be
first on `PATH` and `VIRTUAL_ENV` must point to that environment. Console
scripts installed by the wheel or its declared dependencies must therefore be
available to the tests.

## 5. Test execution

Run the library's complete declared test command in the clean environment.

The library repository controls test content.

The tool owns only execution and result propagation.

## 6. Failure classes

The workflow must clearly fail when:

- package build fails;
- wheel count is not exactly one;
- wheel/dependency installation fails;
- the library test command exits non-zero.

The public workflow does not reinterpret a failed test as success.

## 7. Source-isolation proof

The test environment must prove that the installed wheel is used rather than an
accidental import from the library working tree.

The initial implementation must include an automated test for this behavior.

## 8. Workflow consumption

The public GitHub Actions interface is one reusable workflow callable from
another repository.

Repositories pin one exact released repository revision.

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

- checked-out library commit;
- Python version;
- built wheel filename;
- successful wheel installation;
- library test command;
- final pass/fail.

A separate durable build-store format is not required for the first release.

## 12. Release verification

Before a release is used by another repository:

1. repository tests pass;
2. the tool is released at an exact commit;
3. `tool.py.lib.ci.test` pins that exact release;
4. the external test repository passes.

## 13. Initial repository tests

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


## 14. Superseded run cancellation

The reusable workflow must cancel an older in-progress run when a newer run is
started for the same caller repository, caller workflow and PR/branch.

Different caller repositories, different caller workflows and different
PRs/branches must remain independent.

Consumer repositories must not need to duplicate this normal concurrency
policy.
