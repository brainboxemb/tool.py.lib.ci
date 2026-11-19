# Changelog

## 0.1.1

- replace abstract CI terminology with literal repository/build/test/verify/release language;
- keep the 0.1.0 package-CI behavior unchanged.


## 0.1.0

- add one reusable GitHub Actions workflow for ordinary Python libraries;
- build exactly one wheel from the exact consumer source commit;
- install the wheel and declared dependencies in a clean virtual environment;
- run consumer tests outside the source tree with explicit test-command placeholders;
- propagate build, install and test failures;
- intentionally use no SCons, CAD-CI state or GitHub Actions cache.
