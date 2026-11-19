# Python library CI design

This document describes the implementation architecture for the requirements in
`docs/requirements.md`.

## 1. Public surface

The primary public surface is one reusable GitHub Actions workflow:

```text
.github/workflows/reusable-ci.yml
```

Consumers call that workflow at an exact released commit.

## 2. Thin workflow

The workflow owns only GitHub-hosted setup:

1. checkout the consumer at the exact source SHA;
2. setup the requested Python version;
3. call the repository's package-CI script.

Build/test semantics live in a normal script so they can also be tested locally.

## 3. Package-CI script

Use one small Python script, for example:

```text
scripts/library_ci.py
```

It owns:

- wheel build;
- exactly-one-wheel validation;
- clean virtual environment creation;
- wheel/dependency installation;
- consumer test command execution;
- concise terminal output.

It does not own repository selection, caching or release publication.

## 4. Wheel build

The script builds into a temporary/output directory using standard Python
packaging tooling.

The result is valid only when exactly one wheel exists.

## 5. Clean test environment

Create a new `venv`.

Install the wheel with normal dependency resolution.

Run tests from a working directory that cannot accidentally expose the consumer
package source as an import location.

## 6. Consumer test command

The workflow passes the documented consumer test command to the script.

The command is parsed without a shell and supports:

- `{python}`: clean-environment Python executable;
- `{repo}`: absolute consumer repository root.

The empty/default command is:

```text
{python} -m unittest discover -s {repo}/tests -p test_*.py -v
```

Consumers may override it. Do not embed pytest or unittest policy beyond that
explicit interface.

## 7. No cache/state engine

There is no SCons graph and no GitHub Actions cache.

Every workflow run is intentionally a clean package build/test.

## 8. Release

Release plumbing belongs to this repository, but release publication runs only
after the repository's own tests pass on `main`.

The released repository commit is the public pin used by consumers and by
`tool.py.lib.ci.test`.

## 9. External black-box acceptance

`tool.py.lib.ci.test` calls the released reusable workflow from another
repository.

That acceptance layer proves the public GitHub Actions contract. It must not
reimplement generic package-CI behavior.
