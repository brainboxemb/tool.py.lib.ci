# Python library consumer templates

These are the canonical workflow wrappers for repositories that consume
`tool.py.lib.ci`.

| Template | Purpose |
| --- | --- |
| `ci.yml` | Build and test the exact library package through the public reusable CI workflow. |
| `release.yml` | Owner-issued exact-SHA GitHub release through the public reusable release workflow. |

Each file carries a stable template id and integer template version. The
machine-readable source is [`templates/manifest.json`](../../manifest.json).

Copy the selected template into `.github/workflows/`, replace
`TOOL_PY_LIB_CI_RELEASE_SHA` with one exact externally accepted release, and
change only documented repository-owned values.

A repository-specific release validator is optional. When used it is a Python
script inside the consumer repository and must accept:

```text
--version X.Y.Z
--target-sha <40-character-sha>
--notes-out <path>
```

The validator may enforce package/domain evidence and may write release notes.
Tag creation, GitHub Release creation/idempotency and issue reporting remain
owned by `tool.py.lib.ci`.
