# Mirroring a service — worked example

## When to read this

Step 4 of `add-service`, right before you write the service. The conventions to carry
over are listed in the skill's `Rules → What to do`; this file shows them **applied**
on a neutral example, plus the pitfalls the example exposes.

## Worked example (neutral domain)

The repo has an `OrderService` orchestrating `OrderRepo` + `PricingRepo`, created by an
`OrderServiceFactory`. Task: add a `WidgetService`.

```text
REFERENCE (existing) — order_service:
  OrderServiceFactory.get(variant) -> OrderService(order_repo, pricing_repo)
  class OrderService:
    get(id):       repo read(s) -> compose -> domain object
    search(spec):  validate spec -> repo query -> paginate -> build_result(...)

NEW — widget_service, mirroring it:
  WidgetServiceFactory.get(variant) -> WidgetService(widget_repo, pricing_repo)
  class WidgetService:
    get(id) / search(spec)   # same orchestration shape, same pagination helper
    # data comes only through the repos
```

## Gotchas (what the example exposes)

- **An unregistered service is dead code.** If the repo selects services through a factory/registry, add the new variant in the same place the siblings register — otherwise callers can never reach it.
- **Async/sync must match the reference.** Slipping a blocking call into an async orchestration, or forgetting to await a repo call, is a correctness/perf bug the type checker won't flag.
- **Match the reference's multi-repo failure policy.** When several repos are orchestrated, mirror what it does on a missing dependency — short-circuit, return partial, or raise — rather than inventing a new policy.
