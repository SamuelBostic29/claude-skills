---
name: dto-mapping
version: 1.0.0
description: |
  Generate a family of DTOs and hand-written mapping methods for a .NET entity —
  detail/list/reference read DTOs, create/update input DTOs, and ToDto()-style
  mappers. Use when asked to add DTOs for an entity, build a DTO layer, expose an
  EF Core / domain model through an API surface, or write manual entity↔DTO
  mapping. Reads the model first, recommends only the variants that fit, and
  follows the conventions the codebase already uses instead of imposing its own.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
  - Edit
  - AskUserQuestion
---

# DTO Mapping: generate a DTO family + manual mappers for a .NET entity

You are adding a DTO layer for a .NET entity. Your job is to **read the model first**, recommend the DTO variants that actually fit it, then generate those DTOs and the hand-written mapping methods — in the conventions the codebase already uses, not ones you invent.

The failure mode this skill exists to prevent is the **reflexive 1:1 dump**: a single `<Entity>Dto` mirroring every column, mapped field-by-field, with no thought to whether the caller wants a list row, a reference, or a write payload — and a house style (a mapping library, records, a base type) imposed that the repo never chose. Guard against it from the start: variants come from the model and its callers, and every convention is the adopter's to set.

## When to use this skill

- "Add DTOs for `<entity>`", "create a DTO for this model", "build the DTO layer for X"
- Exposing an EF Core / domain entity through an API and you need read **and** input DTOs
- "Write the mapping", "add `ToDto()` / mapping methods" between an entity and its DTOs
- You have an entity and need the whole family — list row, detail, reference, create/update — not just one DTO

## When NOT to use this skill

- **A DTO already exists and you just need a field added** — edit it directly; this skill scaffolds a family, not one-line tweaks.
- **The repo standardizes on a mapping library** (AutoMapper, Mapster) and wants profiles, not hand-written methods — follow that; this skill writes *manual* mappers. (It can still recommend the variant set.)
- **Non-.NET stacks** — the DTO + mapping idioms here are C#/EF-shaped.
- **Designing the data model, controllers, or endpoints** — out of scope; this is the DTO + mapping layer only.

## Steps

1. **Read the model first.** Locate and read the entity (Glob/Grep/Read). Inventory it: scalars, enums, value objects, to-one and to-many navigations, keys/FKs, audit and server-owned fields, computed members, and anything **sensitive or internal** (password hashes, tokens, soft-delete / row-version flags) that must never reach a DTO. Note nullability. **Generate nothing yet.**

2. **Detect the repo's conventions.** Grep around the model for existing DTOs and mappers and copy the house style: naming (`<Entity>Dto` vs `<Entity>Response` / `Model`), folder + namespace layout, `record` vs `class`, mapping style (instance `ToDto()`, extension method, static factory, or mapper class), nullability stance, and whether inputs are split per operation and carry validation. **What the repo does wins over this skill's defaults.**

3. **Recommend the variants that fit.** Choose from the catalog — read `references/dto-variant-catalog.md` for the menu, the pick-the-variant heuristics, and the mapping-style options. Tie each recommended variant to evidence in the model. Present the set, the conventions you detected, and the chosen mapping style — concisely.

4. **Confirm only what's ambiguous.** If a convention couldn't be read from the repo (no existing DTOs, or mixed styles) or a variant is a judgment call, ask via **AskUserQuestion** — batch the questions, default-first. If everything was detectable, proceed without asking. **Never silently impose a convention the repo didn't show.**

5. **Generate the DTOs.** One file per the repo's grouping; namespace from the repo, or the `<RootNamespace>.<Feature>.Dtos` placeholder when none is detectable. Read DTOs expose only safe, needed fields; **input DTOs exclude server-owned fields** (Id, audit, computed) and carry validation per the repo's convention. Use the detected `record` / `class` style.

6. **Generate the mapping methods.** Hand-written, in the detected style: entity→DTO for each read variant; input→entity for writes — **Create instantiates a new entity; Update mutates the existing tracked entity in place (never `new`)** so EF change-tracking works. Map to-one navigations via their Reference/Detail DTO, to-many via `List<…ListDto>` / `List<…RefDto>`, null-guard optional navigations, and never map a field a variant deliberately omits. **No mapping library.**

7. **Report and stop.** Summarize per Output format. Do **not** build, run, or commit. Stop.

## Output format

Report only the variants you actually generated — you right-size the set, so a line below for a DTO you didn't create would name a file that doesn't exist. Omit any line that doesn't apply.

```
DTOs for <Entity>: <variants chosen>  — <one-line why this set>

Generated (N files):
  <path>/<Entity>Dto.cs          — detail read DTO
  <path>/<Entity>ListDto.cs      — list-row read DTO
  <path>/<Entity>RefDto.cs       — reference DTO
  <path>/Create<Entity>Dto.cs    — create input
  <path>/Update<Entity>Dto.cs    — update input
  <path>/<Entity>Mapping.cs      — hand-written mappers   (style per repo)

Conventions followed: <naming> · <record|class> · <mapping style> · <namespace>
Assumed (no repo precedent): <list, or "none — matched existing DTOs">
Omitted on purpose: <sensitive / server-owned fields left out, and why>

Not done: not built, not committed.
```

## Rules

### What to do

- **Read before you write.** The recommendation must cite the model; never scaffold a DTO family blind.
- **Repo first, catalog second.** Detected conventions outrank this skill's defaults; the catalog is the fallback when the repo is silent.
- **Right-size the set.** Recommend only variants the model and its callers justify — a flat, relation-less entity may need exactly one DTO. Say so; don't ship five.
- **Inputs exclude server-owned fields.** No Id / audit / computed on Create; Update mutates a tracked entity.
- **Every convention is the adopter's.** Naming, `record` vs `class`, mapping style, nullability — offered as configurable opinions, switched to the repo's the instant one is visible.

### What NOT to do

- **NEVER leak sensitive or internal fields** into a read DTO (hashes, tokens, internal flags, row-version / soft-delete). Omit and note it.
- **NEVER blanket-mirror the entity** — a 1:1 DTO per column with every navigation eagerly mapped. That is the failure mode this skill prevents.
- **NEVER pull in a mapping library.** Hand-written mappers only; if the repo standardizes on one, defer (see *When NOT to use*).
- **Don't hardcode** a namespace, base type, or folder — use the detected value or a `<PLACEHOLDER>`.

### Format discipline

- Recommendation and report stay tight and result-first. No preamble, no field-by-field narration of the mapping. Generate, report, stop.

For the variant menu, the pick-the-variant heuristics, the mapping-style options, and a worked example, read `references/dto-variant-catalog.md`.
