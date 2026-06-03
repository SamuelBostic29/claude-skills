---
name: add-service
version: 0.1.0
description: |
  Use when adding the business-logic / service layer for a resource — a service
  class (or a method on one) that orchestrates repositories/DAOs, applies
  validation and business rules, and shapes results, with no HTTP or raw
  persistence code. Triggers: "add a service", "add business logic",
  "orchestrate/compose X", "apply the rules for X", "add a use case". Mirrors the
  nearest existing service; sits above add-data-access and below add-controller.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
  - Edit
  - AskUserQuestion
---

# Add Service: scaffold the business-logic layer by mirroring the repo's existing service

You are adding the service layer for one resource: a service class that orchestrates the repositories/DAOs below it, applies validation and business rules, and shapes results — or a single new method on a service that already exists. Mirror the nearest existing service, then stop. You do not write the persistence (that's the DAO), the route, or the tests.

The failure mode this skill exists to prevent is the **misplaced logic**: business rules smeared into a route handler or a DAO, or a "service" that reaches past its repositories straight into the database/SDK or imports HTTP request/response types. The service is the only layer that holds business logic — and it gets its data exclusively through the repo layer.

## When to use this skill

- "Add a service / business logic / use case for `<Resource>`."
- Orchestrate multiple repositories/DAOs, compose or transform their results.
- Apply validation, cross-entity rules, pagination, or result-shaping.
- Add a method to an existing service.

## When NOT to use this skill

- Pure persistence — a read/write/query — is the **DAO**; use **add-data-access**.
- HTTP routing / request handling is the **controller**; use **add-controller**.
- **Tests** for any layer — use **add-tests**.
- A **trivial pass-through** (the route could call the DAO directly with no logic) and the repo doesn't use a service layer there — don't manufacture one.

## Steps

1. **Find the nearest existing service.** Grep/Glob for the repo's service modules (`service.py`, `*_service.py`, use-case/domain modules). Pick the one most similar to your resource.

2. **Read it whole.** Read the chosen service end to end, plus its factory/wiring and the repositories it depends on. Extract the conventions to match (Rules → What to do).

3. **Confirm the scope.** New service vs a new method on an existing one. If the resource already has a service, add to it — never a parallel class. If the repo dispatches services by variant (a factory/registry), follow that exactly. If ambiguous, ask via AskUserQuestion and stop.

4. **Write the service / method.** Mirror the reference: constructor/DI shape (repos injected), async vs sync style, pagination and result-shaping helpers, the constants block (keep the documented caps and their rationale), error/exception types, and logging. For a concrete orchestration before→after and the boundary checklist, read `references/mirroring-a-service.md`.

5. **Wire it in** (new-service case only) — via the repo's existing factory/DI, the same registration the sibling services use. Do not introduce a new wiring mechanism. Adding a method to an existing service needs no new wiring.

6. **Verify the boundary before finishing.** Confirm the service reaches data only through repositories/DAOs (a missing query is an **add-data-access** task, not inline SQL) and returns domain objects/dicts — never HTTP responses or request parsing.

7. **Stop.** Done = the service (or method) exists, mirrors the reference, and is internally consistent (names/imports resolve by inspection — this skill runs no build). Do not write the DAO, the route, or the tests. Report the files, the service you mirrored, and the repos it orchestrates.

## Output format

Edits/creates files; no console output. Then report exactly:

```
Mirrored: <path to the existing service you matched>
Created/edited: <service path>   (or: added <method> to <service path>)
Orchestrates: <the repos/DAOs it depends on>
Conventions matched: <DI/factory> · <async/sync> · <pagination/result-shaping> · <error types>
Other layers: add-data-access (below) · add-controller (above) · add-tests
```

## Rules

### What to do

- **Mirror, don't invent.** The nearest existing service is the spec — match its idioms, DI shape, and variant-dispatch pattern.
- **Orchestrate, don't persist.** Reach the data exclusively through repositories/DAOs. A missing query is an **add-data-access** task, not an inline SQL call here.
- **One resource, one layer.** A service or a single method. If the resource already has a service, add to it.
- **Keep constants with their rationale.** Mirror the repo's documented caps/limits rather than dropping in bare numbers.

### What NOT to do

- **NEVER put business logic in a route/handler or a DAO** — it belongs in the service.
- **NEVER reach past the repo layer** into the database/SDK directly, or import HTTP request/response types.
- **Don't manufacture a service** for a trivial pass-through the repo would route straight to the DAO.
- **Don't transliterate another language's service idioms** — match this repo's real service.

### Format discipline

- Research before writing. If the repo has no service layer to mirror (controllers call DAOs directly), say so and ask rather than inventing one.
