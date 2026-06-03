# Mirroring tests — worked example

## When to read this

Step 5 of `add-tests`, right before you write the tests. The conventions to carry over
are listed in the skill's `Rules → What to do`; this file shows them **applied** on a
neutral example.

## Worked example (neutral domain)

The repo tests `<OrderService>` in `<tests/test_order_service.py>` using a shared `<FakeOrderRepo>`.
Task: add tests for `WidgetService`.

```text
REFERENCE (existing) — <test_order_service>:
  class TestOrderServiceSearch:
    setup:  OrderService(FakeOrderRepo(seeded rows))
    test_happy_path        -> asserts the composed result
    test_empty_input       -> asserts the empty/short-circuit branch
    test_repo_error_raises -> asserts the error path

NEW — <test_widget_service>, mirroring it:
  reuse the FakeRepo-style fake; same class grouping + naming
  cover: get + search happy path, one meaningful branch, one error path
```

## Gotchas

- A failing test that reveals a real bug: **report it and stop — never edit production code to make the test pass.**
- Reuse the repo's existing fakes/fixtures; don't hand-roll a mock it already provides.
- Mock only the layer directly below the unit — and a **model / pure-function test mocks nothing**, asserting serialization/validation directly.
- Don't run the suite automatically — report the command and let the owner run it.
