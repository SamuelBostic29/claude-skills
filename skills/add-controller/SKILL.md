---
name: add-controller
version: 0.1.0
description: |
  Use when adding the HTTP route/handler (controller) for a resource — wiring an
  endpoint that parses and validates the request, calls the service (or DAO),
  and returns the repo's standardized response, with its auth, error codes, and
  concurrency headers. Triggers: "add an endpoint/route/controller/handler",
  "expose X over HTTP", "add GET/POST /things", "register a route". Mirrors the
  nearest existing handler; sits above add-service and holds no business logic.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
  - Edit
  - AskUserQuestion
---

# Add Controller: scaffold the HTTP layer by mirroring the repo's existing handler

You are adding the route/handler for one resource: the transport adapter that turns an HTTP request into a service (or DAO) call and returns the repo's standardized response. Mirror the nearest existing handler, then stop. You do not write the business logic, the persistence, or the tests.

The failure mode this skill exists to prevent is the **fat controller**: business rules or database calls embedded in the handler, or a hand-rolled auth check, response envelope, and error-code mapping when the repo already has its own. A controller is a thin transport boundary — request in, validate, delegate, standardized response out.

## When to use this skill

- "Add an endpoint / route / controller / handler for `<Resource>`."
- Expose an operation over HTTP (GET/POST/PUT/DELETE).
- Register a new route or blueprint.

## When NOT to use this skill

- **Business logic / orchestration** belongs in the service; use **add-service**.
- **Persistence / queries** belong in the DAO; use **add-data-access**.
- **Tests** for any layer — use **add-tests**.
- A **non-HTTP entry point** (queue/event consumer, CLI, scheduled job) — unless the repo handles those with this same handler pattern, mirror that entry point's own convention instead.

## Steps

1. **Find the nearest existing handler/route** for a similar resource. Grep/Glob the repo's route/handler modules.

2. **Read it whole.** Read the chosen handler end to end, plus how it is registered (blueprint / route-init helper) and the service/factory it calls. Extract the conventions to match (Rules → What to do).

3. **Confirm the scope and the exact routes/verbs.** If the resource already has a handler, add the verb/route to it rather than a parallel one. If anything is ambiguous, ask via AskUserQuestion and stop.

4. **Write the handler/route.** Mirror the reference: the same base (e.g. a `MethodView`/route-init helper), the same DI/constructor, the same verb methods, the same validation → status-code mapping, the same response shaping. For a concrete request-pipeline before→after and the conventions checklist, read `references/mirroring-a-handler.md`.

5. **Register it** (new-handler case only) — exactly as siblings are registered, the same blueprint/url-prefix mechanism. Do not introduce a new registration scheme. Adding a verb/route to an existing handler needs no new registration.

6. **Verify the boundary before finishing.** Confirm the handler only parses/validates the request, delegates to the service (or the DAO, if the repo wires controllers directly to DAOs), and returns the standardized response — with no business rules or SQL leaked in.

7. **Stop.** Done = the routes exist, the handler mirrors the reference, and it is registered the standard way. Do not write the service, the DAO, or the tests. Report the routes, the handler file, the handler you mirrored, and what it calls.

## Output format

Edits/creates files; no console output. Then report exactly:

```
Mirrored: <path to the existing handler/route you matched>
Created/edited: <handler path>; registered at <url prefix / blueprint>
Routes: <VERB /path ...>
Calls: <service/factory, or DAO>
Conventions matched: <auth> · <content-type/validation> · <error codes> · <concurrency headers> · <response shape>
Other layers: add-service (logic) · add-data-access (persistence) · add-tests
```

## Rules

### What to do

- **Mirror, don't invent.** The nearest existing handler is the spec — including how it is registered.
- **Transport only.** Validate the request, map it to a service/DAO call, and return the repo's standardized response with its error-code conventions and concurrency headers (e.g. ETag / `If-Match`).
- **Reuse the repo's auth and response helpers** rather than writing your own.
- **Keep input allowlists aligned** with the layer below — expose only the filters/sorts the service/DAO already allows.

### What NOT to do

- **NEVER put business logic or persistence in the handler** — delegate downward.
- **NEVER hand-roll a new auth scheme, response envelope, or error-code mapping** when the repo has one.
- **Don't widen the input surface** (extra filters/sorts/fields) beyond what the layer below supports.
- **Don't transliterate another framework's controller idioms** — match this repo's real handler.

### Format discipline

- Research before writing. If there is no comparable handler to mirror, ask which entry-point pattern to follow rather than inventing one.
