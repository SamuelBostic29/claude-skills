# Evals for `dto-mapping`

## What this skill is supposed to fix

Without it, "add DTOs for this entity" tends to become a reflexive 1:1 dump — one `<Entity>Dto` mirroring every column, mapped field-by-field, leaking server-owned and internal fields, in whatever house style the model happens to feel like that day. With it, Claude **reads the model first**, recommends a *right-sized* set of variants tied to the model and its callers, follows the repo's existing conventions, and writes hand-written mappers that exclude what shouldn't leak.

## How to run

1. Install: `cp -r skills/dto-mapping ~/.claude/skills/`
2. In a throwaway .NET project, set up each case's working state. Case 1 & 2 use the fixture in [`fixtures/Product.cs`](fixtures/Product.cs).
3. Run the prompt and check against **Expected**. A case passes only if every box holds.

## Cases

### Case 1 — reads the model, recommends a sane set, maps safely (the core case)

- **Setup / fixture:** [`fixtures/Product.cs`](fixtures/Product.cs) — a `Product` with a to-one `Category`, a to-many `Reviews` collection, a server-owned `CreatedUtc`, and an internal `RowVersionHash`.
- **Prompt:** "Add DTOs and mapping for this `Product` entity."
- **Expected:**
  - [ ] **Reads the entity before generating** — the recommendation cites Product's fields/relations, not a blind dump.
  - [ ] Recommends a **sane set**: a detail DTO; a **List DTO** (justified by the `Reviews` collection / columns a list omits); a **Reference DTO** (other entities link to Product); plus **Create + Update** inputs.
  - [ ] Read DTOs **omit `RowVersionHash`** (internal); the **Create input omits `Id` / `CreatedUtc` / `RowVersionHash`**.
  - [ ] Mappers are **hand-written** (`ToDto()` / `ToEntity()`-style) — **no AutoMapper / Mapster**.
  - [ ] **Update mapper mutates a tracked entity in place** (never `new`); Create mapper news up an entity without Id/audit.
  - [ ] To-one `Category` maps via a ref/detail DTO; to-many `Reviews` maps to a `List<…>`, null-guarded.

### Case 2 — portable: placeholder namespaces, asks instead of guessing conventions

- **Setup / fixture:** [`fixtures/Product.cs`](fixtures/Product.cs), in a project with **no existing DTOs** to copy a convention from.
- **Prompt:** "Generate the DTO layer for `Product`."
- **Expected:**
  - [ ] Namespaces/paths are **either the one detectable from the project or a `<RootNamespace>`-style placeholder** — it does **not invent a real company/product namespace** out of nowhere.
  - [ ] With no existing DTO convention found, it **asks** (record vs class, naming, mapping style) **or states the default it is assuming** — it does not silently impose one.
  - [ ] No hardcoded absolute path or real org name appears in the output.

### Case 3 — negative: defers to the repo's mapping library, and right-sizes

- **Setup:** a project that **standardizes on AutoMapper** (a `Profile` class is present), and a trivial entity `Tag { int Id; string Name; }` with no relations.
- **Prompt:** "Add mapping for `Tag`."
- **Expected:**
  - [ ] **Recognizes the repo uses a mapping library and defers** — does not hand-write a manual mapper that fights the AutoMapper convention (per *When NOT to use*).
  - [ ] **Right-sizes:** for a flat, relation-less `Tag`, recommends **one read DTO** (plus inputs only if writes are in play) and says why the list/reference variants aren't warranted — does **not** ship five DTOs.
  - [ ] Treats naming/style as the repo's to set (configurable), not absolutes this skill imposes.
