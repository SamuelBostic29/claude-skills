# Mirroring a DAO — worked example

## When to read this

Step 5 of `add-data-access`, right before you write the model/DAO. The conventions to
carry over are listed in the skill's `Rules → What to do`; this file shows them
**applied**, end to end, on a neutral example.

## Worked example (neutral domain)

The repo already has an `<OrderDAO>` over an `<orders>` store. Task: add data access for `Widget`.

```text
REFERENCE (existing) — <order_dao>:
  class OrderDAO:
    __init__(container, cache, logger, ttl, limits, allowlists, constants...)
    get_by_id(order_id)             # cache-through point read on the partition key
    upsert(payload, if_match=None)  # if_match -> conditional replace; else upsert; then invalidate cache
    delete(order_id, if_match=None) # conditional delete; invalidate item + list caches
    list(tenant, filters, limit, order_by, group_by)
        # allowlist-checked fields -> parameterized query -> optional list-cache + index

NEW — <widget_dao>, mirroring it 1:1:
  class WidgetDAO:
    __init__(...same shape...)
    get_by_id(widget_id)            # same cache-through read
    upsert(payload, if_match=None)  # same concurrency + invalidation
    delete(widget_id, if_match=None)
    list(tenant, filters, limit, order_by, group_by)
        # Widget's own ALLOWED_FILTER / ORDERABLE / GROUPABLE sets, same query/cache builder
```

## Gotchas

- **Match the reference's id derivation exactly** — auto-prefix + uuid, compound from source-key fields, or caller-supplied. Getting it wrong silently creates duplicate or unfindable documents.
- If `Widget` already has a DAO, add the method to it — do not create a second class.
- A new filterable/sortable field must be added to the **allowlist**, or `list` will ignore or reject it.
- Caller-supplied values always go through bound parameters — even a one-off lookup.
- The DAO stays persistence-only: no business rules, no request/response types.
