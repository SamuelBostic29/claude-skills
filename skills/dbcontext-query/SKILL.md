---
name: dbcontext-query
version: 1.0.0
description: |
  Use when asked to generate EF Core data-access methods — get / list / add /
  update / remove / paginate — for an entity, or to scaffold a repository-style
  data layer in a .NET project. A portable .NET/EF Core EXAMPLE you adapt to
  your stack: it reads your repo's conventions, asks for the entity, context,
  scope field, methods, and includes, then emits ONE DbContext partial class
  with exactly the methods requested — every namespace, context, and base type
  left as a placeholder you set.
allowed-tools:
  - Read
  - Grep
  - Glob
  - AskUserQuestion
  - Write
  - Edit
---

# DbContext Query: generate an EF Core data-access partial for one entity

You are turning an entity plus a chosen set of operations into a single `DbContext` partial class of data-access methods. Your job is to **match the repo's existing conventions**, ask only for what you can't infer, emit **exactly the methods requested**, then **STOP for review** — you never build, test, run migrations, or commit.

Two failure modes this skill exists to prevent. First, **drift**: ad-hoc methods that ignore the codebase's async naming, tracking, paging, and — most dangerously — drop the scope/tenant filter, which is a data-leak bug, not a style nit. Second, **law-by-assertion**: treating one team's house style (`Async` suffix, `Add` vs `AddAsync`, soft vs hard delete, throw vs nullable) as universal truth. This is a `.NET`/EF Core **example you adapt** — every style choice is a configurable knob, every namespace/context/base-type a `<PLACEHOLDER>` the adopter sets. Never present one way as the only right way.

## When to use this skill

- "Generate / scaffold EF Core data-access methods for `<Entity>`" — get-by-id, list, add, update, remove, paginate.
- "Add a `DbContext` partial / a repository-style data layer for `<Entity>`."
- Turning an entity and a chosen set of operations into one consistent data-access class.

## When NOT to use this skill

- **Designing the entity, model, or a migration** — this generates *access* methods, not schema. Use EF migrations / your modeling flow.
- **One inline query in a handler** — if it's a single LINQ query used in one place, just write it; don't scaffold a partial.
- **Non-EF data access** (Dapper, raw SQL, another ORM) — these signatures are EF Core-specific; adapt by hand instead.
- **A repo that already source-generates / T4-generates its data layer** — extend that generator, don't hand-emit alongside it.

## Steps

1. **Find the data layer.** Grep/Glob for the `DbContext` (`: DbContext`), existing `partial class <Context>` files, and data-access methods on a similar entity. Record the conventions you can *detect* — async-method suffix, return shape (`Task<T?>` vs throw-on-missing), tracking default (`AsNoTracking` on reads?), how paging is represented (a `PagedResult<T>`-style wrapper), how the scope/tenant filter is applied, `Add` vs `AddAsync`, explicit-type vs `var`. **Detected conventions override every default below.**

2. **Settle the inputs — ask only what research didn't.** Via AskUserQuestion, batching related questions (≤4 per prompt), confirm or collect:
   - **Entity & key** — the entity type and its key type (and `DbSet`, if not inferable).
   - **Context & namespace** — the `DbContext` class, its namespace, and the target file.
   - **Scope field** — the field that scopes reads (e.g. `CategoryId`, `TenantId`, `OwnerId`), or *none*.
   - **Methods** — which of get-by-id / list / add / update / remove / paginate / exists to emit.
   - **Includes, tracking, delete** — navigations to eager-load; reads tracked or `AsNoTracking`; delete soft or hard.

   **Never invent the entity, context, namespace, or scope field.** If research didn't settle one and the user didn't say, ask and stop.

3. **Confirm the context is `partial`.** The target must be declared `partial class <Context>`. If the main context file isn't `partial`, add the keyword (Edit) or flag it — otherwise the generated file won't compile.

4. **Generate exactly the requested methods.** Read `references/method-signatures.md` for the signature catalog and the annotated worked example. Emit one partial-class file containing **only** the methods chosen in step 2 — no kitchen-sink. Apply the scope filter to every multi-row read; eager-load the chosen includes; honor the tracking and soft/hard-delete knobs; give paginated/list reads a deterministic `OrderBy`. Use the conventions detected in step 1; for anything still unknown, leave an `<ANGLE_BRACKET>` placeholder — **never a guessed real value**.

5. **Write, report, and stop.** Write `<Context>.<Entity>.cs` (or merge into the existing partial via Edit), then report per Output format. **Do not build, test, run migrations, or commit** — generation stops at a written file for review. Stop here.

## Output format

A written `.cs` file, plus a verdict-first report — the result line first:

```
Generated <path>/<DbContext>.<Entity>.cs — <N> methods: <comma-separated list>
Conventions: <detected | default> — async-suffix=<…>, reads=<AsNoTracking | tracked>, delete=<soft | hard>, scope=<field | none>
Placeholders left to fill: <surviving <ANGLE_BRACKET>s, or "none">
Not done: not built, not tested, not committed — review, then wire it in.
```

## Rules

### What to do

- **Match the repo over the default.** Conventions detected in step 1 win; the defaults here only fill gaps.
- **Generate only what was asked.** Emit exactly the chosen methods. Hard rule — no bonus methods "for completeness."
- **Always apply the scope filter** to multi-row reads (list / paginate / exists-in-scope) when a scope field was given. A missing tenant/owner filter is a data-leak bug, not a style choice.
- **`AsNoTracking` on reads by default;** track only when the caller mutates-and-saves. Configurable — flip it if the repo tracks by default.
- **Deterministic ordering before paging.** `Skip`/`Take` without a stable `OrderBy` returns arbitrary rows.

### What NOT to do

- **NEVER state a convention as universal fact.** `Async` suffix, `Add` vs `AddAsync`, save-in-method vs unit-of-work, soft vs hard delete, nullable-return vs throw — each is an adopter knob, presented with its trade-off, never "the correct way."
- **NEVER hardcode a real namespace, context, schema, or table** in the catalog or example. Placeholders only; the neutral domain is Product / Category.
- **NEVER emit a kitchen-sink** of methods nobody requested.
- **Don't build, test, run migrations, or commit.** The deliverable is a file for review.

### Format discipline

- Verdict line first (file + method count), then the convention and placeholder summary. No preamble, no narrating the research.

For the full signature catalog and the annotated worked example, read `references/method-signatures.md`.
