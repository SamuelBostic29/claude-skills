# Mirroring a handler — worked example

## When to read this

Step 4 of `add-controller`, right before you write the route/handler. The conventions to
carry over are listed in the skill's `Rules → What to do`; this file shows them **applied**
on a neutral example, plus the pitfalls the example exposes.

## Worked example (neutral domain)

The repo has an `OrderHandler` mounted at `/orders`. Task: add `/widgets`.

```text
REFERENCE (existing) — order_handler (MethodView / route-init helper):
  pipeline: auth -> validate content-type -> parse payload -> validate -> call OrderService -> respond(envelope)
  GET  /orders/<id>     # returns ETag
  PUT  /orders/<id>     # requires If-Match -> precondition-failed on mismatch
  registered: register_blueprint(order_bp, url_prefix=<prefix>)

NEW — widget_handler, mirroring it:
  same auth/validate/respond pipeline, same error-code mapping, same ETag/If-Match handling
  GET/POST/PUT/DELETE /widgets
  registered the same way, same url-prefix mechanism
```

## Gotchas (what the example exposes)

- **Concurrency is half-applied if you only read it.** Return the ETag on reads *and* require `If-Match` on writes — emitting the header without enforcing it silently drops optimistic-concurrency protection. Note the split across layers: the handler owns the HTTP precondition (read `If-Match`, return precondition-failed on mismatch) and passes the version down; the **DAO** performs the actual conditional write (see `add-data-access`) — two halves of one flow, not two implementations.
- **Status codes must match the sibling's mapping.** A one-off code (415 where the repo uses 400, 409 where it uses 412) breaks client expectations even when the logic is correct.
- **Validate shape here, rules in the service.** The handler checks content-type, required fields, and types; business validation belongs to the service — split it wrong and checks get duplicated or dropped.
