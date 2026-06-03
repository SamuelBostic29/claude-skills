# Mirroring a service — worked example

## When to read this

Step 4 of `add-service`, right before you write the service. The conventions to carry
over are listed in the skill's `Rules → What to do`; this file shows them **applied**
on a neutral example.

## Worked example (neutral domain)

The repo has an `<OrderService>` orchestrating `<OrderRepo>` + `<PricingRepo>`, created by
`<OrderServiceFactory>`. Task: add `WidgetService`.

```text
REFERENCE (existing) — <order_service>:
  OrderServiceFactory.get(variant) -> OrderService(order_repo, pricing_repo)
  class OrderService:
    get(id):       repo read(s) -> compose -> domain object
    search(spec):  validate spec -> repo query -> paginate -> build_result(...)

NEW — <widget_service>, mirroring it:
  WidgetServiceFactory.get(variant) -> WidgetService(widget_repo, pricing_repo)
  class WidgetService:
    get(id) / search(spec)   # same orchestration shape, same pagination helper
    # NO HTTP types, NO direct DB/SDK calls — data comes only through the repos
```

## Gotchas

- Need data the repo can't return yet? Add the query via `add-data-access` — don't inline SQL here.
- The service returns domain objects/dicts, never an HTTP response.
- Keep the documented caps and *why* they exist; don't drop in bare numbers.
- If the repo has no service layer (controllers call DAOs directly), stop and ask rather than inventing one.
