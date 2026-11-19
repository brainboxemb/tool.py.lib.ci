# Repository plan

This file contains only current unfinished work for `tool.py.lib.ci`.

Requirements live in `docs/requirements.md`. Architecture lives in
`docs/design.md`.

## 1. Expose installed command scripts during tests — #5

Prepare release 0.1.2.

- run tests with the clean environment's executable directory first on PATH;
- set VIRTUAL_ENV to the clean environment;
- preserve source-tree isolation;
- prove an installed console script is visible during tests;
- keep build/install/test failure handling unchanged.

After repository tests pass:

1. release 0.1.2 from the tested main commit;
2. update `tool.py.lib.ci.test` to exact 0.1.2 commit;
3. pass the external test repository;
4. remove this section and close #5.

Library repositories that use this tool are tracked in their own plans.
