# Changelog

## 0.1.0

- add one reusable GitHub Actions workflow for ordinary Python libraries;
- build exactly one wheel from the exact consumer source commit;
- install the wheel and declared dependencies in a clean virtual environment;
- run consumer tests outside the source tree with explicit test-command placeholders;
- propagate build, install and test failures;
- intentionally use no SCons, CAD-CI state or GitHub Actions cache.
