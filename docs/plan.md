# Repository plan

This file contains only current unfinished work for `tool.py.lib.ci`.

Requirements live in `docs/requirements.md`. Architecture lives in
`docs/design.md`.

## 1. Implement the 0.1.1 package-CI core — #2

Implement the first reusable Python-library CI path:

- reusable GitHub Actions workflow;
- exact library checkout;
- Python version input;
- one-wheel build;
- clean virtual environment;
- install wheel with declared dependencies;
- run library tests;
- clear build/install/test failures;
- no SCons;
- no CAD-CI;
- no GitHub Actions cache.

Add direct repository tests for every initial repository-test requirement.

## 2. Release 0.1.1

After repository tests are green:

- add explicit version/release metadata;
- publish release 0.1.1 from the exact tested main commit;
- document the exact release commit.

Remove this section after the release exists.

## 3. Test the released version externally

Update `brainboxemb/tool.py.lib.ci.test` to pin the exact 0.1.1 release.

Do not use the released version in another repository until the external test repository passes.

## 4. Migrate the first library repository

After the external test passes, migrate
`brainboxemb/lib.py.cad.verfication` away from `tool.cad.ci`/SCons and onto
the accepted `tool.py.lib.ci` release.

The migration itself is tracked in that repository.
