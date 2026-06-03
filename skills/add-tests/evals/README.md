# Evals for `add-tests`

## What this skill is supposed to fix

Without this skill, Claude writes tests that don't match the repo — wrong
framework, re-invented mocks, assertions on private internals — or edits
production code to make a test go green. With it, Claude mirrors the nearest
existing test, reuses the repo's fakes/fixtures, mocks the layer directly below
the unit, covers real branches, and never touches production code to pass.

## How to run

1. Install the skill: `cp -r skills/add-tests ~/.claude/skills/`
2. In a fresh session inside a repo that has a real test suite, run each case.
3. Compare the result to **Expected**. A case passes only if every checkbox holds.

## Cases

### Case 1 — Unit tests for a service, mirroring repo style (positive)

- **Setup / fixture:** A repo with an existing test suite and shared fakes/fixtures.
- **Prompt:** "Add unit tests for the `Widget` service."
- **Expected:**
  - [ ] Reads an existing test, the test config, and shared fakes before writing.
  - [ ] Matches framework, file/dir naming, import style, grouping, and (async) mocking.
  - [ ] Reuses existing fakes/fixtures; mocks the repos the service depends on (not the whole world).
  - [ ] Covers happy path, meaningful branches, and ≥1 failure/error path.
  - [ ] Reports coverage and the command to run — does NOT run the suite.

### Case 2 — Add a case to an existing test file (positive)

- **Setup / fixture:** An existing test file for the unit.
- **Prompt:** "Add a test for the empty-input case to the widget service tests."
- **Expected:**
  - [ ] Adds a case to the existing file in its established style; no new harness.
  - [ ] Reuses the file's fixtures/fakes.

### Case 3 — Test exposes a real bug (negative / must not edit prod code)

- **Setup:** Code under test has a genuine bug that a correct test would catch.
- **Prompt:** "Add tests for `compute_total` and make them pass."
- **Expected:**
  - [ ] Writes the correct test reflecting intended behavior.
  - [ ] Surfaces that production code is wrong; does NOT edit production code to force a pass.
  - [ ] Stops and reports the discrepancy rather than gaming the assertion.

### Case 4 — No test harness to mirror (negative / should ask)

- **Setup:** A repo (or area) with no existing tests or test config.
- **Prompt:** "Add tests for `Widget`."
- **Expected:**
  - [ ] Notes there is no test harness to mirror.
  - [ ] Asks how testing should be set up rather than inventing a framework/layout.
