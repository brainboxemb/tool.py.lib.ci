# Changelog

## 0.2.1

- create missing release tags explicitly as annotated Git tag objects before
  creating the GitHub Release;
- reject an existing lightweight release tag instead of silently accepting a
  weaker tag shape;
- verify the annotated tag resolves to the exact stable-head release commit.


## 0.2.0

- add a public reusable Python-library release workflow for owner-issued
  `/release vX.Y.Z <sha>` requests;
- publish or idempotently verify one exact stable-head Git tag and GitHub
  Release, failing closed when an existing tag points elsewhere;
- add an optional repository-owned Python validator hook receiving version,
  target SHA and release-notes output path before publication;
- add canonical versioned CI and release consumer templates plus
  `docs/new-library.md` onboarding;
- keep generic GitHub release transaction in the tool while leaving
  package/domain qualification in the consumer validator.


## 0.1.5

- classify safely comparable non-forced push events for documentation-only package-CI skipping;
- fail safe to full CI for forced pushes, zero/invalid before SHAs and explicit source overrides;
- expose `change_scope` (`docs-only` or `full`) as a reusable-workflow output for caller-owned downstream policy;
- preserve NUL-delimited changed paths and rename-disabled Git comparison semantics.

## 0.1.4

- keep the reusable CI check successful for pull requests that change only files below `docs/`;
- skip setup-python and package build/install/test for that conservative docs-only case;
- fail safe to full package CI for pushes, explicit source overrides, mixed/empty/unknown changes, and any path outside `docs/`;
- classify changed paths centrally with rename detection disabled and print the skip reason.

## 0.1.3

- cancel superseded reusable Python-library CI runs for the same caller repository, workflow and PR/branch;
- keep different caller scopes independent;
- keep the concurrency policy inside the reusable workflow so consumers do not duplicate it.

## 0.1.2

- run library tests with the clean virtual environment active through PATH and VIRTUAL_ENV;
- make console scripts installed by the wheel or its dependencies available during tests;
- keep source-tree imports isolated.


## 0.1.1

- replace abstract CI terminology with literal repository/build/test/verify/release language;
- keep the 0.1.0 package-CI behavior unchanged.


## 0.1.0

- add one reusable GitHub Actions workflow for ordinary Python libraries;
- build exactly one wheel from the exact library source commit;
- install the wheel and declared dependencies in a clean virtual environment;
- run library tests outside the source tree with explicit test-command placeholders;
- propagate build, install and test failures;
- intentionally use no SCons, CAD-CI state or GitHub Actions cache.
