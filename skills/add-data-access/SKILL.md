---
name: add-data-access
version: 1.0.0
description: |
  Use when adding the data-access layer for a resource — a typed model plus a
  repository/DAO class, or one new read/write/query method on a DAO that already
  exists. Triggers: "add data access", "add a DAO/repository", "read/write the
  data store for an entity", "add a query method". This is the
  bottom layer only: it mirrors the nearest existing DAO and stops before the
  service, route, and test layers (see add-service / add-controller / add-tests).
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
  - Edit
  - AskUserQuestion
---

# Add Data Access: scaffold the persistence layer by mirroring the repo's existing DAO

You are adding the data-access layer for one resource: a typed model and its repository/DAO, or a single new method on a DAO that already exists. Your job is to produce persistence code that is indistinguishable in shape from the nearest existing DAO in this repo, then stop — you do not build the service layer, the route/controller, or the tests.

The failure mode this skill exists to prevent is the **textbook DAO**: generating a clean, generic data-access class from memory (or transliterated from another language's ORM) that ignores how *this* repo actually does persistence — its concurrency control, cache keys, query parameterization, and partition/primary-key handling. Mirror the real code; never invent a parallel pattern.

## When to use this skill

- "Add data access / a DAO / a repository for `<Resource>`."
- "Read / write / query the `<store>` for `<Resource>`" — a new persistence operation.
- "Add a `get_by_<field>` / list / upsert / delete method" to an existing DAO.
- You need to persist or fetch an entity and there is no DAO method for it yet.

## When NOT to use this skill

- The work is **business logic / orchestration** (validation, cross-entity rules, transforms) — that's the service layer; use **add-service**.
- The work is an **HTTP endpoint / route / request handling** — use **add-controller**.
- The work is **tests** for any layer — use **add-tests**.
- It's a **one-off script query** that won't live in the codebase — write it inline; don't manufacture a DAO.

## Steps

1. **Find the nearest existing DAO.** Grep/Glob for the repo's data-access modules (files named like `*_dao`, `*repository*`, `*store*`, or whatever this repo uses). Pick the one most similar to the resource you're adding — same store, same partitioning shape.

2. **Read it whole.** Read the chosen DAO end to end, plus its model/entity definition. Extract the conventions you must match (the checklist in Rules → What to do). If one convention is ambiguous, read a second DAO before writing.

3. **Confirm the scope.** Decide whether this is a **new model + DAO** or **one new method** on an existing DAO. If the resource already has a DAO, default to adding a method to it — never create a parallel class. If which existing DAO to mirror is genuinely unclear, ask via AskUserQuestion and stop.

4. **Write the model** (new-DAO case only). Define the typed model exactly as the repo defines its models — same base type, field-typing style, timestamp/serialization handling.

5. **Write the DAO / method.** Mirror the reference's structure: constructor/dependency shape, primary-key & partition handling, optimistic-concurrency mechanism, cache keys + invalidation, parameterized queries, field allowlists, the constants block, and logging. Keep it persistence-only — no business rules, no request/response types. For a concrete before→after and the full conventions-to-match checklist, read `references/mirroring-a-dao.md`.

6. **Wire it in only as the repo already wires DAOs** (the same registration/factory the sibling DAO uses). Do not introduce a new wiring mechanism.

7. **Stop.** Done = the model and DAO (or the new method) exist, mirror the reference, and import/compile cleanly. Do not write the service, the route, or the tests — those are separate skills. Report the files and the reference DAO you mirrored.

## Output format

Edits/creates files; no console output. Then report exactly:

```
Mirrored: <path to the existing DAO you matched>
Created/edited: <model path>, <dao path>   (or: added <method> to <dao path>)
Conventions matched: <pk/partition> · <concurrency> · <cache+invalidation> · <param queries> · <allowlists>
Other layers: add-service (logic) · add-controller (HTTP) · add-tests
```

## Rules

### What to do

- **Mirror, don't invent.** The nearest existing DAO is the spec. Match its idioms even if you'd personally write it differently.
- **Match every persistence convention the reference encodes:** primary-key / `id` derivation, partition-key handling, optimistic concurrency (e.g. ETag / `If-Match`), cache namespace + key shape + invalidation, query **parameterization**, filter/order/group **allowlists**, the constants / no-magic-numbers block, and the logging prefix/format.
- **One resource, one layer.** A model + its DAO, or a single method. If the resource already has a DAO, add to it rather than creating a second class.
- **Keep the layer boundary clean.** Persistence only — reads/writes/queries and their caching. No validation, business rules, or HTTP types.

### What NOT to do

- **NEVER interpolate caller-supplied values into a query string.** Use the repo's parameterization, always — even when a quick f-string "would work."
- **NEVER invent a new caching, concurrency, or wiring scheme** when the repo already has one. Reuse it.
- **Don't transliterate another language's ORM/repository idioms.** Produce code idiomatic to this repo, matched to its real DAO — not a port of muscle memory.
- **Don't bleed upward.** No business logic, no route/HTTP concerns, no test code — those belong to add-service / add-controller / add-tests.

### Format discipline

- Research before writing: never emit a DAO before reading a real one in this repo. If there is no existing DAO to mirror, say so and ask how to proceed — do not invent a house style.
