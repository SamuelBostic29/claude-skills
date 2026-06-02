# DTO variant + mapping-method catalog — layer-3 reference

## When to read this

Step 3 of `SKILL.md` sends you here — to pick the DTO variants that fit the model, and the mapping-method style. Treat everything below as **configurable defaults**: the moment the repo shows an existing convention (step 2), that convention wins.

## Variant catalog

| Variant | Typical name | When to use it | Notes / gotchas |
|---|---|---|---|
| **Detail / full read** | `<Entity>Dto` | Single-item reads (GET by id), detail screens | Scalars + selected nested Reference/child DTOs. Still omit sensitive/internal fields. |
| **List / summary read** | `<Entity>ListDto` | Collection endpoints, tables, grids | Slim — only the columns the list renders. **No heavy nested collections** (overfetch / N+1). |
| **Reference / lookup** | `<Entity>RefDto` | When *other* entities point at this one, or it nests inside other DTOs; dropdowns | Usually just Id + a display label. Keeps object graphs from ballooning. |
| **Create input** | `Create<Entity>Dto` | POST bodies | Only client-settable fields. **No Id / audit / computed.** Validation per repo convention. |
| **Update input** | `Update<Entity>Dto` | PUT / PATCH bodies | Full replace (PUT) vs partial (PATCH). For partial, see the tri-state note below. |
| **Patch input** *(optional)* | `Patch<Entity>Dto` | PATCH partial updates only | Tri-state problem: "field absent" ≠ "field set to null". Use JSON Patch or nullable wrappers; don't fake it with plain nullables. |

## Pick-the-variant heuristics

- **One read DTO is enough when** the entity is flat (few fields, no/one relation) and the list and detail views would be identical. Ship one; say why the others aren't needed.
- **Add a List DTO when** detail carries collections or columns a list view doesn't need.
- **Add a Reference DTO when** other entities reference this one, or it appears nested inside other DTOs.
- **Split Create vs Update when** server-owned fields differ between the two operations, or update is partial.
- **Skip any variant nothing consumes.** Don't ship speculative DTOs — right-sizing is the point.

## Mapping-method style options

| Style | Shape | When it fits |
|---|---|---|
| **Extension methods** | `public static <Entity>Dto ToDto(this <Entity> e)` in a `*MappingExtensions` static class | Keeps the entity clean and the DTO assembly separate. The common default in layered apps. |
| **Instance method on entity** | `public <Entity>Dto ToDto()` on the entity | Simplest call site, but the domain assembly must reference the DTOs. |
| **Static factory on the DTO** | `public static <Entity>Dto FromEntity(<Entity> e)` | The DTO owns its own construction. |
| **Dedicated mapper class** | `<Entity>Mapper` with `ToDto` / `ToEntity` | Mapping has real logic, DI dependencies, or is unit-tested in isolation. |

> No mapping library. If the repo standardizes on AutoMapper / Mapster, this skill defers — see *When NOT to use* in `SKILL.md`.

## Mapping rules

- **Read (entity → DTO):** map to-one navigations via their Reference (or Detail) DTO; map to-many to `List<…ListDto>` / `List<…RefDto>`. **Null-guard optional navigations.** Never map a field the variant deliberately omits.
- **Create (input → new entity):** set only client-settable fields; let the DB / domain assign Id, audit, and computed values.
- **Update (input → existing entity):** load the tracked entity and **mutate it in place** — never `new` it, or EF change-tracking breaks. For partial updates, assign only the fields actually provided.

## Worked example

Neutral domain. Namespaces are `<RootNamespace>` placeholders the adopter fills in.

**Input — the entity:**

```csharp
namespace <RootNamespace>.Catalog.Domain;

public class Product
{
    public int Id { get; set; }
    public string Name { get; set; } = "";
    public string? Description { get; set; }
    public decimal Price { get; set; }
    public int CategoryId { get; set; }
    public Category Category { get; set; } = null!;            // to-one
    public ICollection<ProductReview> Reviews { get; set; } = new List<ProductReview>(); // to-many
    public DateTime CreatedUtc { get; set; }                   // server-owned
    public string RowVersionHash { get; set; } = "";           // internal — never expose
}
```

**Recommended set:** detail + list + reference reads, plus create/update inputs.
Detail needs the category (as a ref) and reviews (as a slim list); the list view doesn't need reviews; other entities link to products, so a ref DTO earns its place. `CreatedUtc` is exposed read-only; `RowVersionHash` is omitted everywhere.

**Output — DTOs (record style shown):**

```csharp
namespace <RootNamespace>.Catalog.Dtos;

public record ProductDto(
    int Id,
    string Name,
    string? Description,
    decimal Price,
    CategoryRefDto Category,
    IReadOnlyList<ProductReviewListDto> Reviews,
    DateTime CreatedUtc);

public record ProductListDto(int Id, string Name, decimal Price, string CategoryName);

public record ProductRefDto(int Id, string Name);

public record CreateProductDto(string Name, string? Description, decimal Price, int CategoryId);

public record UpdateProductDto(string Name, string? Description, decimal Price, int CategoryId);
```

**Output — mappers (extension-method style shown):**

```csharp
namespace <RootNamespace>.Catalog.Dtos;

public static class ProductMappingExtensions
{
    public static ProductDto ToDto(this Product e) => new(
        e.Id, e.Name, e.Description, e.Price,
        e.Category.ToRefDto(),
        e.Reviews.Select(r => r.ToListDto()).ToList(),
        e.CreatedUtc);

    public static ProductListDto ToListDto(this Product e) =>
        new(e.Id, e.Name, e.Price, e.Category.Name);

    public static ProductRefDto ToRefDto(this Product e) => new(e.Id, e.Name);

    // create: input -> NEW entity (Id / CreatedUtc / RowVersionHash set server-side)
    public static Product ToEntity(this CreateProductDto dto) => new()
    {
        Name = dto.Name,
        Description = dto.Description,
        Price = dto.Price,
        CategoryId = dto.CategoryId,
    };

    // update: mutate the TRACKED entity in place — never `new`
    public static void Apply(this UpdateProductDto dto, Product e)
    {
        e.Name = dto.Name;
        e.Description = dto.Description;
        e.Price = dto.Price;
        e.CategoryId = dto.CategoryId;
    }
}
```

The snippet shows `Product`'s mappers only — `e.Category.ToRefDto()` and `r.ToListDto()` call the *related* types' own mappers (`Category` → `CategoryRefDto`, `ProductReview` → `ProductReviewListDto`), defined alongside those types, so it isn't self-contained/compilable.

Note what the mappers do *not* touch on update: `Id`, `CreatedUtc`, `RowVersionHash` — server-owned and internal, never set from a client payload.
