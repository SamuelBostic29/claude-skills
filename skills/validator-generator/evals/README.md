# Evals for `validator-generator`

## What this skill is supposed to fix

Without it, asking for a validator yields a *plausible-but-ungrounded* one: rules for properties the DTO doesn't have, a persistence stack (`DbContext`, `IMediator`, Dapper) named inline, or an update uniqueness check that rejects the record's own unchanged value. With it, every rule maps to a real property, async checks go through an adopter-owned abstraction (FluentValidation stays the only named third-party type), and update/shared-save uniqueness excludes the current row.

## How to run

1. Install: `cp -r skills/validator-generator ~/.claude/skills/`
2. In a fresh session, give the skill the fixture DTO below (paste it, or drop it in a scratch `.cs`).
3. Run each case's prompt and check the result against **Expected**. A case passes only if every box holds.

**Fixture DTO** (neutral; `Id` distinguishes create from update):

```csharp
public sealed class SaveProductDto
{
    public int? Id { get; set; }       // null/0 = create, set = update
    public string Name { get; set; }
    public decimal Price { get; set; }
    public int CategoryId { get; set; }
}
```

## Cases

### Case 1 — create: grounded rules + async uniqueness via an abstraction

- **Prompt:** "Generate a create validator for `SaveProductDto`. Name must be unique and CategoryId must exist."
- **Expected:**
  - [ ] One `RuleFor` per **real** property (`Name`, `Price`, `CategoryId`) — no invented fields, `Id` not required on the create path
  - [ ] Uniqueness and FK-existence are `MustAsync` rules calling an **injected adopter-owned abstraction** (e.g. `IProductUniquenessChecker`), not a `DbContext`/repository implementation
  - [ ] **FluentValidation is the only named third-party type** in the file (`AbstractValidator`/`IValidator` are FluentValidation's own; the injected check interface is a placeholder the adopter owns)
  - [ ] Base type, namespace, and the abstraction are placeholders; neutral domain only
  - [ ] Max length / message wording emitted as defaults and **flagged configurable**

### Case 2 — update: uniqueness EXCLUDES self (signature correctness)

- **Prompt:** "Now the update variant for the same DTO."
- **Expected:**
  - [ ] `Id` is required (`GreaterThan(0)` / `NotEmpty`)
  - [ ] Uniqueness uses the overload that passes `Id` so the check **excludes the current record** (does not flag the row's own unchanged name)
  - [ ] Does **not** silently reuse the create-path uniqueness call (which would be the signature bug)

### Case 3 — portability across every variant (the acceptance eval)

- **Prompt:** "Generate the validator for `SaveProductDto` as each variant: create, update, delete, shared-save, and import."
- **Expected:** for **every** variant produced —
  - [ ] **create** — structural + uniqueness, no `Id` requirement
  - [ ] **update** — `Id` required + uniqueness excluding self
  - [ ] **delete** — `Id` required + a dependency/in-use check via the abstraction
  - [ ] **shared-save** — one validator, `When(...)` branch on `Id` (create-rules unset, update-rules excl. self when set)
  - [ ] **import** — `RuleForEach(...).SetValidator(...)`, non-empty batch, and a cross-row duplicate check
  - [ ] **In all five, FluentValidation is the only named third-party dependency**; base type / namespace / data abstractions remain placeholders; no real entity or stack names

### Case 4 — incomplete or wrong-tech request → ask / defer, don't guess

- **Setup / prompts:**
  - (a) "Add a validator." (no DTO, no variant, no checks named)
  - (b) "Add DataAnnotations `[Required]` attributes to this DTO."
  - (c) "Make a validator" pointed at a type that doesn't exist yet.
- **Expected:**
  - [ ] (a) Asks for the **DTO, the variant, and the uniqueness/dependency checks** before writing anything — does not invent a variant or rules
  - [ ] (b) Recognizes this is not FluentValidation and **defers** (this skill emits FluentValidation only)
  - [ ] (c) Stops and says the DTO must exist first, rather than inventing a shape
