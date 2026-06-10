# Evals for `py-check`

## What this skill is supposed to fix

Without this skill, "check my changes" in DPTH either runs nothing (CI gives false
confidence — it has no test/lint steps at all), runs tests with the wrong toolchain
(bare `pytest` outside the conda env → ModuleNotFoundError chaos), or runs ruff
repo-wide and buries the 3 findings the change caused under hundreds of legacy ones.
With it, Claude gates exactly the affected service(s) with the right toolchain,
scopes lint to the diff, and reports a verdict in terms a .NET developer can act on.

## How to run

1. Install the skill: `cp -r skills/py-check ~/.claude/skills/`
2. In a fresh session inside the DPTH clone
   (`C:\Users\Samuel.Bostic\Documents\Paradigm\Repos\Backend\Data Plane Transaction Hub`),
   set up each case's working-tree state by hand, then run the prompt.
3. Compare the result to **Expected**. A case passes only if every checkbox holds.

## Cases

### Case 1 — single-service change, full gate

- **Setup / fixture:** edit one file under `txservices/apis/handlers/` (e.g. add an
  unused local variable to provoke a ruff F841); working conda env `txservices`.
- **Prompt:** "/py-check"
- **Expected:**
  - [ ] Runs the txservices suite via `conda run -n txservices ... python -m pytest tests -q`
        from `txservices/apis` (not bare pytest, not from repo root)
  - [ ] Runs `uvx ruff check` on ONLY the changed file(s) — never `ruff check .` or repo-wide
  - [ ] Does not gate search or mulesoft
  - [ ] Verdict-first output with the table; the F841 finding appears with `file:line`
        and flips the verdict to FAIL
  - [ ] Makes no edits — no `--fix`, no `# noqa`, no config files created

### Case 2 — mulesoft change with a failing test, translated

- **Setup / fixture:** edit a `mulesoft/src/` file so one existing test fails.
- **Prompt:** "check my python changes before I open the PR"
- **Expected:**
  - [ ] Tests run via `uv run pytest tests -q` from `mulesoft`
  - [ ] mypy runs on changed files only, with `--follow-imports=silent
        --ignore-missing-imports`, and is reported as advisory — it does NOT flip the verdict
  - [ ] The failing test gets a plain-English explanation with `file:line` and a cause
        hypothesis (read the test body if pytest output is cryptic), not a raw traceback dump
  - [ ] Verdict FAIL comes from the test, with a one-line "what to do next"

### Case 3 — negative: broken environment is BLOCKED, not FAIL

- **Setup:** remove the `search` conda env (`conda env remove -n search`); edit a file
  under `search/apis/`.
- **Prompt:** "/py-check"
- **Expected:**
  - [ ] Reports BLOCKED for search (not FAIL), names the missing env, and points to `/py-env`
  - [ ] Does NOT create the env, pip-install anything, or fabricate a pass/fail for tests it couldn't run

### Case 4 — negative: clean tree, no silent full-repo sweep

- **Setup:** no uncommitted changes; branch even with `origin/main`.
- **Prompt:** "/py-check"
- **Expected:**
  - [ ] States there are no changed `.py` files to gate
  - [ ] Asks which service's full suite to run (AskUserQuestion) instead of running
        everything or lint-sweeping the repo
