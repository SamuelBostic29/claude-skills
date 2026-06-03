# Mirroring a handler — worked example

## When to read this

Step 4 of `add-controller`, right before you write the route/handler. The conventions to
carry over are listed in the skill's `Rules → What to do`; this file shows them **applied**
on a neutral example.

## Worked example (neutral domain)

The repo has an `<OrderHandler>` mounted at `/orders`. Task: add `/widgets`.

```text
REFERENCE (existing) — <order_handler> (MethodView / route-init helper):
  pipeline: auth -> validate content-type -> parse payload -> validate -> call OrderService -> respond(envelope)
  GET  /orders/<id>     # returns ETag
  PUT  /orders/<id>     # requires If-Match -> precondition-failed on mismatch
  registered: register_blueprint(order_bp, url_prefix=<prefix>)

NEW — <widget_handler>, mirroring it:
  same auth/validate/respond pipeline, same error-code mapping, same ETag/If-Match handling
  GET/POST/PUT/DELETE /widgets
  registered the same way, same url-prefix mechanism
```

## Gotchas

- A new business rule belongs in the service (`add-service`), not the handler.
- Don't expose a filter/sort the layer below doesn't already allow.
- Reuse the response and error helpers — don't invent a new envelope or status mapping.
- The handler holds no persistence: it calls the service (or the DAO, if the repo wires controllers straight to DAOs).
