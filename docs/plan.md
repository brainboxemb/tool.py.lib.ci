# Repository plan

This file contains only current unfinished work for `tool.py.lib.ci`.

Requirements live in `docs/requirements.md`. Architecture lives in
`docs/design.md`.

## 1. Implement the 0.1.0 package-CI core

Implement the first reusable Python-library CI path:

- reusable GitHub Actions workflow;
- exact consumer checkout;
- Python version input;
- one-wheel build;
- clean virtual environment;
- install wheel with declared dependencies;
- run consumer tests;
- clear build/install/test failures;
- no SCons;
- no CAD-CI;
- no GitHub Actions cache.

Add direct repository tests for every initial acceptance requirement.

## 2. Release 0.1.0

After repository tests are green:

- add explicit version/release metadata;
- publish release 0.1.0 from the exact tested main commit;
- document the exact release commit.

Remove this section after the release exists.

## 3. Qualify 0.1.0 externally

Update `brainboxemb/tool.py.lib.ci.test` to pin the exact 0.1.0 release.

Do not consider 0.1.0 consumer-ready until the black-box acceptance repository
passes.

## 4. First consumer cut-over

After external acceptance passes, migrate
`brainboxemb/lib.py.cad.verfication` away from `tool.cad.ci`/SCons and onto
the accepted `tool.py.lib.ci` release.

The consumer migration itself is tracked in that repository.
