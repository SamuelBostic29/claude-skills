# Evals for `dbcontext-query`

## What this skill is supposed to fix

Without it, "add data-access methods for this entity" yields ad-hoc EF Core code that drifts from the codebase — inconsistent async naming and tracking, a guessed-at paging shape, sometimes a **dropped scope/tenant filter** (a data leak), and a kitchen-sink of methods nobody asked for. With it, Claude detects the repo's conventions, asks only for what it can't infer, and emits **one partial class with exactly the requested methods** — every namespace/context/base-type a placeholder the adopter sets, no team convention asserted as universal.

## How to run

1. Install: `cp -r skills/dbcontext-query ~/.claude/skills/`
2. Set up each case's working state (a throwaway .NET project, or just the prompt).
3. Run the prompt and check against **Expected**. A case passes only if every box holds.

## Cases

### Case 1 — happy path: neutral entity, exact method subset

- **Setup:** a project with a `CatalogContext : DbContext` and a `Product` entity (key `int`, a `CategoryId`, a `Category` navigation).
- **Prompt:** "Generate EF Core data-access methods for `Product` in `CatalogContext` — get-by-id, list by `CategoryId`, add, and paginate; include `Category`."
- **Expected:**
  - [ ] Confirms entity, context, scope field, methods, and includes before generating
  - [ ] Emits **exactly four** methods (get-by-id, list, add, paginate) — no Update/Remove/Exists bonus
  - [ ] List and paginate **filter by `CategoryId`** (scope applied)
  - [ ] Reads use `AsNoTracking`; `Category` is eager-loaded; paginate has a deterministic `OrderBy`
  - [ ] Output is **one `partial class CatalogContext`** file; did NOT build, test, or commit

### Case 2 — matches the repo's conventions; no convention asserted as law

- **Setup:** the repo already has `OrderData.cs` with `partial class ShopContext`, using **no `Async` suffix**, **explicit types**, reads **without `AsNoTracking`**, and a `Page<T>` paging wrapper.
- **Prompt:** "Add the same kind of data-access methods for `Product`."
- **Expected:**
  - [ ] Matches the detected style — no `Async` suffix, explicit types, the repo's `Page<T>` type, reads tracked
  - [ ] Does **NOT** impose `Async`/`AsNoTracking` as "the correct way" against the repo's style
  - [ ] Namespace and context name come **from the repo**, not invented
  - [ ] Anything genuinely unknown is left as an `<ANGLE_BRACKET>` placeholder, not a guessed value

### Case 3 — negative: asks instead of guessing

- **Setup:** a bare prompt with no entity/context/scope given and no obvious data layer in the repo.
- **Prompt:** "Add some EF data-access methods."
- **Expected:**
  - [ ] Asks (entity & key, context & namespace, scope field, methods, includes) via AskUserQuestion
  - [ ] Does **NOT** invent an entity, namespace, or context, and does **NOT** write a guessed file
  - [ ] Stops pending answers rather than generating

### Case 4 — decision-rule: soft-delete knob, only what was asked

- **Setup:** a `Product` entity with `IsDeleted` and `DeletedUtc` fields.
- **Prompt:** "Generate just a soft-delete remove for `Product`."
- **Expected:**
  - [ ] Emits **only** a remove method — no list/add/paginate bonus
  - [ ] Soft delete: loads the entity **tracked**, sets `IsDeleted` and `DeletedUtc = DateTime.UtcNow`
  - [ ] Does **NOT** also hard-`Remove` the entity (honors the chosen soft/hard knob)
