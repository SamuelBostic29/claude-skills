# Mirroring tests — worked example

## When to read this

Step 5 of `add-tests`, right before you write the tests. The conventions to carry over
are listed in the skill's `Rules → What to do`; this file shows them **applied** on a
neutral example, plus the pitfalls the example exposes.

## Worked example (neutral domain)

The repo tests `OrderService` in `tests/test_order_service.py` using a shared `FakeOrderRepo`.
Task: add tests for `WidgetService`.

```text
REFERENCE (existing) — test_order_service:
  class TestOrderServiceSearch:
    setup:  OrderService(FakeOrderRepo(seeded rows))
    test_happy_path        -> asserts the composed result
    test_empty_input       -> asserts the empty/short-circuit branch
    test_repo_error_raises -> asserts the error path

NEW — test_widget_service, mirroring it:
  reuse the FakeRepo-style fake; same class grouping + naming
  cover: get + search happy path, one meaningful branch, one error path
```

## Gotchas (what the example exposes)

- **A model / pure-function test mocks nothing.** Routing it through a mock just tests the mock, not the code — assert its serialization/validation directly.
- **Match the reference's async-test style.** Asserting on an un-awaited coroutine, or using a sync mock for an async dependency, yields false greens that pass while the real path is broken.
- **Seed fakes through the real contract.** A fake that returns a shape the real dependency never would makes the test pass while the integration silently breaks; mirror the shapes the production repo/service actually returns.
