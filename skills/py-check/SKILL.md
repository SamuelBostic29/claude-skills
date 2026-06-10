---
name: py-check
version: 1.0.0
description: |
  Pre-PR quality gate for the Data Plane Transaction Hub repo: run the affected
  service's test suite (txservices, search, mulesoft/Rx) plus ruff — and mypy
  where declared — scoped to the files you changed, and translate failures into
  plain terms for .NET developers. Use when asked to "check my python changes",
  "/py-check", "run the tests" in DPTH, or before opening a DPTH PR. DPTH CI
  runs no tests and no lint, so this gate is the only safety net.
allowed-tools:
  - Read
  - Grep
  - Glob
  - AskUserQuestion
  - Bash(git:*)
  - Bash(conda:*)
  - Bash(uv:*)
  - Bash(uvx:*)
  - Bash(python:*)
---

# Py-check: the pre-PR test + lint gate for DPTH

DPTH's CI builds are manual and run **no tests, no lint, no type checks** — whatever you don't catch locally ships. Your job is to run the right checks for the service(s) the current changes touch, then report a verdict a .NET developer can act on. Two failure modes to guard against: running lint repo-wide (this codebase has never been linted — repo-wide ruff produces hundreds of legacy findings that bury the three caused by today's change), and silently "fixing" what you find (this skill reports; fixing is a separate, explicit ask).

## When to use this skill

- "/py-check", "check my changes", "run the tests" while working in DPTH
- Before `draft-pr` / opening a PR on DPTH
- "Did I break anything?" after editing txservices, search, or mulesoft code

## When NOT to use this skill

- **.NET or frontend repos** — use `dotnet test` / the repo's own scripts; this matrix is DPTH-specific.
- **Setting up or repairing the Python environment** — use `/py-env`; if a check fails because the env is broken (conda env missing, ModuleNotFoundError on install), stop and point there.
- **Live end-to-end verification against a running service** — that's `/api-verify`'s job; py-check never starts services.
- **Auto-fixing findings** — only on an explicit "fix them" after the report.

## The check matrix

Repo root: `C:\Users\Samuel.Bostic\Documents\Paradigm\Repos\Backend\Data Plane Transaction Hub`

| Service (path prefix) | Tests (full suite — they're fast) | Lint (changed files only) | Types (changed files only) |
|---|---|---|---|
| `txservices/` | `conda run -n txservices --no-capture-output python -m pytest tests -q` from `txservices/apis` | `uvx ruff check <files>` | — (not declared; skip) |
| `search/` | `conda run -n search --no-capture-output python -m pytest tests -q` from `search/apis` | `uvx ruff check <files>` | — (not declared; skip) |
| `mulesoft/` | `uv run pytest tests -q` from `mulesoft` | `uv run ruff check <files>` | `uv run mypy --follow-imports=silent --ignore-missing-imports <files>` (advisory) |

Notes baked into the matrix:

- txservices/search tests are `unittest.TestCase`-style but `pytest` is in both `requirements.txt` files and runs them natively. Tests import relative to the `apis/` dir — always run from there.
- ruff and mypy are declared dev deps **only** in `mulesoft/pyproject.toml`. For the conda services, `uvx ruff check` runs ruff without polluting their envs; if uv isn't installed, mark lint SKIPPED with a one-line note — don't pip-install tools into service envs.
- mypy flags exist because the repo has no mypy config and largely untyped code: `--follow-imports=silent --ignore-missing-imports` keeps the signal on the changed files. mypy findings are **advisory** — they never fail the gate.
- There is no ruff/pytest/mypy config anywhere in the repo. Run defaults; never create config files to tune results.

## Steps

1. **Compute the changed set.** From the DPTH repo: `git diff --name-only origin/main...HEAD` plus staged/unstaged (`git status --porcelain`), filtered to `*.py`. Map files to services by path prefix. If the user named a service explicitly, gate that service regardless of the diff.

2. **Pick the scope.**
   - Changes in one service → gate that service.
   - Changes span services → gate each affected service, one at a time.
   - No changed `.py` files and no service named → say there's nothing to gate and ask (AskUserQuestion) which service's full suite to run, or stop if the user just wanted confirmation.

3. **Run the gate per service** (Bash tool, native exes directly — no `cmd.exe` wrapper; one call per check so failures attribute cleanly):
   - Full test suite per the matrix.
   - `ruff check` on the changed files in that service only.
   - mypy (mulesoft only) on the changed files, advisory.
   - Environment errors (env missing, imports failing at collection) are not test failures — stop the service's gate, report BLOCKED, and point at `/py-env`.

4. **Translate failures.** For each failing test or lint finding, one plain-English line: what broke, where (`file:line`), and the likely cause in terms a .NET dev knows (e.g. "`assert_called_once_with` mismatch — the Moq `Verify` equivalent failed: the handler now passes 3 args"). Read the failing test body when the pytest output alone doesn't explain it.

5. **Report the verdict** in the Output format below. Gate result: PASS only if all tests pass and ruff reports zero findings on changed files; mypy never flips the verdict.

6. **Stop.** Done = verdict reported. Do not fix findings, do not re-run to "confirm", do not start services. If the user says "fix them", that's the next task, not this skill.

## Output format

```
py-check: <PASS | FAIL | BLOCKED> — <service(s)>, <N> changed .py files

| Service    | Tests            | Ruff (changed files) | Mypy (advisory) |
|------------|------------------|----------------------|-----------------|
| txservices | 33 passed        | 2 findings           | —               |
| mulesoft   | 121 passed, 1 F  | clean                | 3 notes         |

Failures:
1. mulesoft tests/test_customer_aging_service.py:88 — test_aging_buckets: expected 4 buckets, got 5.
   The composer now emits a "90+" bucket; the test's expected list needs the new bucket (or the change is wrong).
2. txservices ruff F841 apis/handlers/txn_handler.py:212 — local `result` assigned but never used.

Verdict: FAIL — fix the bucket expectation mismatch; the ruff findings are one-line cleanups.
```

## Rules

### What to do

- **Full test suite, changed-file lint.** Suites here are small and fast — run them whole; lint only what the diff touches.
- **Attribute before reporting.** A failure line always carries `file:line` and a cause hypothesis, not just the assertion dump.
- **Distinguish BLOCKED from FAIL.** Broken environment → BLOCKED + `/py-env`; broken code → FAIL.
- **Run checks in the service's own toolchain** — conda env for txservices/search, uv for mulesoft. `uvx` only for tools the service doesn't declare.

### What NOT to do

- **NEVER run ruff or mypy repo-wide.** Legacy noise buries the findings the change caused. Changed files only — hard rule.
- **NEVER edit code, test expectations, or config during the gate.** Report only; fixing is a separate explicit ask. No `# noqa`, no `--fix`, no new config files.
- **Don't install lint/type tools into the service conda envs.** They're not declared deps; use `uvx` or skip.
- **Don't fail the gate on mypy.** Advisory only — the codebase is untyped; treating mypy as a gate would block every PR.

### Format discipline

- Verdict line first, table second, failure explanations third. Nothing else.
- A clean run is the verdict line and the table — no celebration, no suggestions.
