# Validator patterns — the five variants, annotated

## When to read this

Step 4 of `SKILL.md` sends you here once the variant is known. Read the matching section, mirror its shape, and substitute the repo's real base type, namespace, and abstractions for the placeholders. The example domain is neutral on purpose (`Product` / `Category` / `Order`) — never carry these names into generated code; use the adopter's DTO.

## Pick the variant

| Variant | Guards | Signature concern |
|---|---|---|
| **create** | a brand-new entity | required fields; **uniqueness** (value free); FK existence |
| **update** | mutating an existing entity | `Id` required; **uniqueness excluding self**; optional concurrency token |
| **delete** | removing an entity | `Id` required; **dependency / in-use** check (block if still referenced) |
| **shared-save** | create + update through one DTO | branch on `Id`: create-rules when unset, update-rules (excl. self) when set |
| **import** | a batch of rows | `RuleForEach` per row; **cross-row** uniqueness within the batch; non-empty |

## Where async checks get their data

Uniqueness, FK-existence, and dependency checks must hit a data source. Inject an **adopter-owned abstraction** — a small interface the adopter implements over their repository/`DbContext`/query — **never a named third-party type**. That is what keeps FluentValidation the only named third-party dependency in the validator. The interfaces below are neutral examples the adopter owns; swap in the repo's real ones:

- `IProductUniquenessChecker` — the cross-record questions the create/update rules ask: `Task<bool> IsNameAvailableAsync(string name, CancellationToken ct)`, an `(string name, int excludingId, CancellationToken ct)` overload for update, and `Task<bool> CategoryExistsAsync(int categoryId, CancellationToken ct)` for the FK-existence rule.
- `IProductDependencyChecker` — `Task<bool> IsReferencedByOrdersAsync(int id, CancellationToken ct)`.

The genuine fill-ins — angle-bracketed because the adopter must supply them — are `<Namespace>` (the validators' namespace) and the base type: `AbstractValidator<T>` (FluentValidation's own, safe to name) or the repo's `<BaseValidator<T>>` if it has one.

> **Order rules cheapest-first.** Structural rules (`NotEmpty`, `MaximumLength`, range) run before any `MustAsync`, so a malformed request never reaches the database. `Cascade(CascadeMode.Stop)` on a property enforces that; it is configurable.

## create

```csharp
namespace <Namespace>;

using FluentValidation;

public sealed class CreateProductValidator : AbstractValidator<CreateProductDto>   // or : <BaseValidator<CreateProductDto>>
{
    public CreateProductValidator(IProductUniquenessChecker uniqueness)
    {
        RuleFor(x => x.Name)
            .Cascade(CascadeMode.Stop)        // first failure wins for this property (older FluentValidation: StopOnFirstFailure) — opinion
            .NotEmpty()
            .MaximumLength(200)               // length is an opinion — set to the column/domain limit
            .MustAsync((name, ct) => uniqueness.IsNameAvailableAsync(name, ct))
            .WithMessage("A product named '{PropertyValue}' already exists.");

        RuleFor(x => x.Price)
            .GreaterThan(0);

        RuleFor(x => x.CategoryId)
            .GreaterThan(0)
            .MustAsync((id, ct) => uniqueness.CategoryExistsAsync(id, ct))   // FK existence — through the abstraction, not a DbContext
            .WithMessage("Category {PropertyValue} does not exist.");
    }
}
```

## update

The only structural difference from create is `Id`, but the uniqueness check is fundamentally different: it must **exclude the row being edited**, or saving a record without changing its name fails as "already taken." Use the four-argument `MustAsync` overload so you can read the DTO's `Id`.

```csharp
public sealed class UpdateProductValidator : AbstractValidator<UpdateProductDto>
{
    public UpdateProductValidator(IProductUniquenessChecker uniqueness)
    {
        RuleFor(x => x.Id).GreaterThan(0);

        RuleFor(x => x.Name)
            .NotEmpty()
            .MaximumLength(200)
            // 4-arg overload (root, value, context, ct): we need the whole DTO to pass Id.
            // EXCLUDING the current row is the #1 update-validator bug — do not omit it.
            .MustAsync((dto, name, _, ct) => uniqueness.IsNameAvailableAsync(name, dto.Id, ct))
            .WithMessage("Another product named '{PropertyValue}' already exists.");
    }
}
```

## delete

Usually just an `Id` plus a **dependency check** — refuse the delete while the entity is still referenced. Note the negation: the rule passes when the entity is *not* referenced.

```csharp
public sealed class DeleteProductValidator : AbstractValidator<DeleteProductDto>
{
    public DeleteProductValidator(IProductDependencyChecker dependencies)
    {
        RuleFor(x => x.Id)
            .GreaterThan(0)
            .MustAsync(async (id, ct) => !await dependencies.IsReferencedByOrdersAsync(id, ct))
            .WithMessage("This product can't be deleted while it is referenced by existing orders.");
    }
}
```

## shared-save

One DTO carries both create and update. Branch on `Id`: unset (`null`/`0` for `int?`, `Guid.Empty` for `Guid`) means create; set means update. Shared structural rules sit outside the branches; only the uniqueness rule differs.

```csharp
public sealed class SaveProductValidator : AbstractValidator<SaveProductDto>
{
    public SaveProductValidator(IProductUniquenessChecker uniqueness)
    {
        // Shared structural rules — apply to both paths.
        RuleFor(x => x.Name).NotEmpty().MaximumLength(200);
        RuleFor(x => x.Price).GreaterThan(0);

        // Create path: no Id yet.
        When(x => !x.Id.HasValue || x.Id.Value == 0, () =>
        {
            RuleFor(x => x.Name)
                .MustAsync((name, ct) => uniqueness.IsNameAvailableAsync(name, ct))
                .WithMessage("A product named '{PropertyValue}' already exists.");
        });

        // Update path: Id present — uniqueness must EXCLUDE this row.
        When(x => x.Id.HasValue && x.Id.Value > 0, () =>
        {
            RuleFor(x => x.Id).GreaterThan(0);
            RuleFor(x => x.Name)
                .MustAsync((dto, name, _, ct) => uniqueness.IsNameAvailableAsync(name, dto.Id!.Value, ct))
                .WithMessage("Another product named '{PropertyValue}' already exists.");
        });
    }
}
```

*(For a `Guid` key, branch on `x.Id == Guid.Empty`; for a non-nullable `int` default, on `x.Id == 0`.)*

## import

A batch DTO holds rows. Compose the **per-row** validator with `RuleForEach(...).SetValidator(...)`, require the batch non-empty, and add a **cross-row** rule for in-batch duplicates. Prefer deferring per-row *database* uniqueness to one batched query in the handler over firing N `MustAsync` calls — flag that as an opinion.

```csharp
using System.Linq;
using FluentValidation;

public sealed class ImportProductsValidator : AbstractValidator<ImportProductsDto>
{
    public ImportProductsValidator(IValidator<ProductImportRow> rowValidator)   // IValidator<T> is FluentValidation's own — safe to name
    {
        RuleFor(x => x.Rows).NotEmpty();

        RuleForEach(x => x.Rows).SetValidator(rowValidator);

        // Cross-row: names must be unique WITHIN the batch (case-insensitive).
        RuleFor(x => x.Rows)
            .Must(rows => rows
                .GroupBy(r => r.Name, StringComparer.OrdinalIgnoreCase)
                .All(g => g.Count() == 1))
            .WithMessage("Duplicate product names within the import file.")
            .When(x => x.Rows is not null);
    }
}

public sealed class ProductImportRowValidator : AbstractValidator<ProductImportRow>
{
    public ProductImportRowValidator()
    {
        RuleFor(x => x.Name).NotEmpty().MaximumLength(200);
        RuleFor(x => x.Price).GreaterThan(0);
    }
}
```

## Opinions to tune (defaults, not law)

Emit sensible defaults and tell the adopter these are configurable:

- **Lengths / ranges** — `MaximumLength(200)`, `GreaterThan(0)`: match the column and domain.
- **Messages** — wording and the `{PropertyName}` / `{PropertyValue}` placeholders; localize if the repo does.
- **Cascade mode** — `Cascade(CascadeMode.Stop)` (first failure) vs. collect-all; set per the repo's convention.
- **Import DB-uniqueness** — per-row `MustAsync` (N queries) vs. one batched check in the handler.
- **Casing / format** — regex and string rules are domain choices.

## Wiring (note it; edit only if asked)

- **Assembly scan:** `services.AddValidatorsFromAssemblyContaining<SaveProductValidator>();` — no per-validator registration.
- **Explicit:** `services.AddScoped<IValidator<SaveProductDto>, SaveProductValidator>();`

Whether validation runs automatically (a pipeline behavior / filter) is a handler concern — out of scope for this skill.
