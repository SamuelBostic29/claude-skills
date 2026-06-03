---
name: add-tests
version: 0.1.0
description: |
  Use when adding tests for code in this repo — unit tests for a model, DAO,
  service, or handler, mirroring the repo's existing test style (framework,
  layout, mocking, fixtures). Triggers: "add tests", "write unit tests for X",
  "cover this with tests", "add a test case". Mirrors the nearest existing test,
  mocks the layer directly below, and never edits production code to pass.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
  - Edit
  - AskUserQuestion
---

# Add Tests: scaffold tests by mirroring the repo's existing test style

You are adding tests for one unit of code — a model, DAO, service, or handler — that match how this repo already writes tests. Mirror the nearest existing test, then stop. You write tests; you do not change production code, and you do not run the suite (you report the command to run it).

The failure mode this skill exists to prevent is **tests that don't belong to this repo**: wrong framework or layout, re-inventing mocks the repo already provides, asserting private implementation detail instead of behavior — or worst of all, quietly editing production code so a test goes green. Mirror the real tests, mock the layer directly below the unit, and assert observable behavior.

## When to use this skill

- "Add tests / unit tests for `<X>`."
- Cover a new model / DAO / service / handler with tests.
- Add a case to an existing test file.

## When NOT to use this skill

- You actually need to **change production code** (a bug fix) — do that first; tests come after.
- You need **manual / integration verification of the running app** — that's a run/verify task, not unit tests.
- The repo has **no test setup at all** — ask how testing should be established rather than inventing a harness.

## Steps

1. **Find the nearest existing test** for a similar layer/resource. Grep/Glob the repo's tests (`test_*.py`, `*_test.*`, `*.spec.*`, etc.).

2. **Read it whole.** Read the chosen test plus the test config and shared helpers (e.g. `conftest.py`, `pyproject.toml`/`pytest.ini`, fixtures, fakes). Extract the conventions to match (Rules → What to do).

3. **Read the code under test.** Cases must reflect its real behavior, branches, and error paths — not guessed ones.

4. **Confirm the scope.** A new test file vs cases added to an existing one. If ambiguous, ask via AskUserQuestion and stop.

5. **Write the tests.** Mirror the reference: framework, file/dir naming, import style, class/function grouping, and mocking (sync vs async). Reuse the repo's existing fakes/fixtures rather than re-inventing them. Mock only the layer directly below the unit. Cover the happy path, the meaningful branches, and at least one failure/error path. For a concrete before→after and the conventions checklist, read `references/mirroring-tests.md`.

6. **Never modify production code to make a test pass.** If the code looks untestable or wrong, surface it and stop — do not "fix" it under cover of writing a test.

7. **Stop.** Done = the tests exist and mirror the reference. Report the test file(s), what's covered, and the command to run them. Do not run the suite automatically.

## Output format

Edits/creates files; no console output. Then report exactly:

```
Mirrored: <path to the existing test you matched>
Created/edited: <test path>   (or: added cases to <test path>)
Covers: <units / branches / error paths>
Reused: <existing fixtures/fakes>
Run with: <the repo's test command>   (not run automatically)
```

## Rules

### What to do

- **Mirror, don't invent.** Match the nearest test's framework, layout, naming, and mocking style.
- **Mock the layer directly below the unit.** A service test fakes its repos; a handler test fakes the layer directly below it — its service, or its DAO if the handler calls one directly; a model / pure-function test mocks nothing and asserts its serialization/validation directly. Reuse the repo's existing fakes/fixtures.
- **Cover behavior that matters.** Happy path, the meaningful branches, and ≥1 failure/error path.
- **Assert observable behavior and contracts** — return values, calls made, errors raised — not private internals.

### What NOT to do

- **NEVER modify production code to make a test pass.** Fix the code separately, or surface the problem and stop.
- **Don't re-invent a mock or fixture the repo already provides.**
- **Don't auto-run the suite** — report the command and let the owner run it.
- **Don't write brittle tests** coupled to internals, call order that doesn't matter, or exact log strings.

### Format discipline

- Research before writing. If the repo has no test harness to mirror, ask how to set one up rather than inventing one.
