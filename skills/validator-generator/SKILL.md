---
name: validator-generator
version: 1.0.0
description: |
  Generate a FluentValidation validator for a .NET DTO or command — create,
  update, delete, shared-save, or import variant — with rules grounded in the
  DTO's real properties and the repo's existing validator conventions.
  Uniqueness and dependency checks go through an adopter-owned abstraction, so
  FluentValidation stays the only named third-party dependency. Use when asked
  to write/generate/add a validator or "add validation for <DTO>".
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
  - Edit
  - AskUserQuestion
---

# Validator Generator: generate one FluentValidation validator for one DTO

You are generating a FluentValidation validator for a single .NET DTO/command. Your job is to read the DTO's actual shape and the repo's existing validators, then emit one validator whose rules mirror that reality — the right variant (create / update / delete / shared-save / import), with uniqueness and dependency checks wired through an adopter-owned abstraction.

The failure mode this skill exists to prevent is the **plausible-but-ungrounded validator**: rules invented for properties the DTO doesn't have, a persistence stack (EF Core, MediatR, Dapper, a `DbContext`) hardcoded by name, or — the signature correctness bug — an *update* uniqueness check that flags the record's own unchanged value as already taken. Ground every rule in the DTO and the repo's conventions; never invent validation, never name a stack.

## When to use this skill

- "Write / generate / add a validator for `<DTO>`" / "add validation for this command"
- Scaffolding FluentValidation rules for a create / update / delete / shared-save / import operation
- You have a DTO or command type and need its `AbstractValidator<T>` with the right variant rules

## When NOT to use this skill

- **No DTO yet** — if the type to validate doesn't exist, write it first; this skill validates an existing shape.
- **Non-FluentValidation validation** — DataAnnotations attributes, manual `if` guards, or a different library. This skill emits FluentValidation only.
- **Debugging an existing validator's logic** — open it and edit directly; this skill authors new validators. (To understand how a validator is used across the call chain, use `call-trace`.)
- **Business orchestration** — side effects, multi-step transactions, cross-aggregate workflows. Those belong in the handler, not a validator.

## Steps

1. **Get the three inputs up front.** Via AskUserQuestion if they aren't already clear: (a) the **DTO/command** to validate — point me at the type or file; (b) the **variant** — create / update / delete / shared-save / import; (c) the **uniqueness & dependency checks** this operation needs (e.g. "name must be unique", "category must exist", "block delete if referenced by orders"). If any of the three is missing or ambiguous, ask and stop — never guess the variant or invent checks.

2. **Read the DTO.** Open the type and list its real properties, CLR types, and nullability. Every `RuleFor` you emit maps to a property that actually exists — no invented fields.

3. **Learn the repo's conventions.** Grep/Glob for existing `AbstractValidator<` usages. Capture: the base validator type (often a custom `<BaseValidator<T>>`, else `AbstractValidator<T>`), namespace and folder layout, file naming (`{Dto}Validator.cs`), cascade mode, message style, and how async checks reach data (injected repository, a dedicated checker interface, etc.). Mirror what you find. If there are none, fall back to the patterns reference and flag each style choice as an opinion the adopter can change.

4. **Read the patterns reference.** Once the variant is known, read `references/validator-patterns.md` for the annotated shape of that variant — including the create-vs-update uniqueness difference and the cross-row import rules.

5. **Generate the validator.** Emit one `{Dto}Validator` class:
   - **Structural rules** per property (required / length / range / format), drawn from the DTO's types and nullability.
   - **Variant-specific rules** per the reference (e.g. `Id` required on update/delete; `When(...)` branches for shared-save; `RuleForEach` for import).
   - **Uniqueness/dependency checks** as `MustAsync` rules calling an **adopter-owned placeholder abstraction** injected via the constructor (e.g. `IProductUniquenessChecker`). Never name EF Core, MediatR, Dapper, or a `DbContext`. On **update / shared-save**, pass the entity's Id so the check **excludes the current record**.
   - Keep universal opinions (max lengths, message wording, cascade mode, casing) clearly marked as configurable.

6. **Place the file.** Write `{Dto}Validator.cs` to the repo's validators location with the matching namespace. If the adopter registers validators explicitly (no assembly scan), note the one-line DI registration — and add it via Edit only if asked.

7. **Report & stop.** State the file written, the variant, the property rules, and every injected abstraction the adopter must implement or bind. List any style choices you made as configurable. Do not build, run, or commit. Stop.

## Output format

The deliverable is the validator file. Report this, then stop:

```
Validator: <path>/{Dto}Validator.cs   (variant: create | update | delete | shared-save | import)
Validates: <Dto> — <N> property rules
Async checks: <each MustAsync rule> via <IAdopterAbstraction>  (you implement/bind this)
Conventions: matched <existing validators> | none found — used defaults (flagged below)
Configurable opinions: <max lengths / messages / cascade — what to tune>
DI: <explicit registration line, or "auto via assembly scan">

Not done for you: not built, not registered (unless asked), not committed.
```

## Rules

### What to do

- **Ground every rule in the DTO.** One `RuleFor` per real property; types and nullability drive required/length/range. Never validate a field the DTO doesn't have.
- **Match the repo before the reference.** Existing validators define the base type, namespace, naming, and async-check style — mirror them. The reference is the fallback when there are none.
- **Update uniqueness excludes self.** The signature bug is an update/save validator that rejects the record's own unchanged value. Always pass the Id so the check ignores the current row.
- **Async checks through an adopter-owned abstraction.** Inject a small adopter-owned interface (e.g. `IProductUniquenessChecker` / `IProductRepository`) for uniqueness / dependency / FK-existence. Keep FluentValidation the only *named* third-party type.
- **Flag opinions as opinions.** Max lengths, message wording, cascade mode, casing — emit sensible defaults and say they're tunable.

### What NOT to do

- **NEVER invent rules or properties** absent from the DTO, or constraints you can't ground in the type or a stated check.
- **NEVER hardcode a persistence stack** — no `DbContext`, `IMediator`, Dapper, repository implementation, connection, or real entity names. Placeholders only.
- **NEVER ship an update/shared-save uniqueness check that doesn't exclude the current record.**
- **Don't put business orchestration in the validator** — side effects, transactions, and cross-aggregate workflows belong in the handler.
- **Don't auto-build, run, or commit.** The deliverable is the file plus the report.

### Format discipline

- Report the file path and the abstractions the adopter must supply, plainly and first. No preamble, no narrating the research.

For the annotated per-variant catalog (create / update / delete / shared-save / import) on a neutral Product/Category domain, read `references/validator-patterns.md`.
