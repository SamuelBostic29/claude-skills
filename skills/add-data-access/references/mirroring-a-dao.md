# Mirroring a DAO — worked example

## When to read this

Step 5 of `add-data-access`, right before you write the model/DAO. The conventions to
carry over are listed in the skill's `Rules → What to do`; this file shows them
**applied**, end to end, on a neutral example, plus the pitfalls the example exposes.

## Worked example (neutral domain)

The repo already has an `OrderDAO` over an `orders` store. Task: add data access for a `Widget`. (This example uses a partitioned, cached store, so it exercises the full checklist; a plain SQL/ORM repo has fewer conventions — mirror only what your reference actually uses.)

```text
REFERENCE (existing) — order_dao:
  class OrderDAO:
    __init__(container, cache, logger, ttl, limits, allowlists, constants...)
    get_by_id(order_id)             # cache-through point read on the partition key
    upsert(payload, if_match=None)  # if_match -> conditional replace; else upsert; then invalidate cache
    delete(order_id, if_match=None) # conditional delete; invalidate item + list caches
    list(tenant, filters, limit, order_by, group_by)
        # allowlist-checked fields -> parameterized query -> optional list-cache + index

NEW — widget_dao, mirroring it 1:1:
  class WidgetDAO:
    __init__(...same shape...)
    get_by_id(widget_id)            # same cache-through read
    upsert(payload, if_match=None)  # same concurrency + invalidation
    delete(widget_id, if_match=None)
    list(tenant, filters, limit, order_by, group_by)
        # Widget's own ALLOWED_FILTER / ORDERABLE / GROUPABLE sets, same query/cache builder
```

## Gotchas (what the example exposes)

- **Id derivation is silent when wrong.** Match the reference exactly — auto-prefix + uuid, compound from source-key fields, or caller-supplied. A mismatch produces duplicate or unfindable documents with no error.
- **A new filter/sort field stays inert until it's in the allowlist.** `list` ignores fields it doesn't recognize, so the query "succeeds" but never actually filters or orders by it.
- **Changing a partition-key value strands the old document.** A plain upsert with a new partition value leaves the prior copy under its old partition — check how the reference re-partitions (delete-then-write) before touching a key field.
