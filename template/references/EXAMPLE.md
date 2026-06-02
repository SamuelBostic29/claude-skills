# <Reference title> — layer-3 reference file

<!--
============================================================================
This file demonstrates the LAYER 3 of progressive disclosure (the "appendix").

Put content here that is:
  - large (a full catalog, signature table, or set of worked examples), AND
  - only needed once the skill is actively doing its job — not to decide
    whether to trigger.

The SKILL.md body stays lean and points here on demand, e.g.:
    "For the full variant catalog, read `references/EXAMPLE.md`."
That way this content costs zero context until it's actually needed.

Rename this file to something descriptive (e.g. `dto-variant-catalog.md`,
`method-signatures.md`). Delete this whole comment block and the references/
folder entirely if your skill doesn't need a layer-3 reference.
============================================================================
-->

## When to read this

<One line: the SKILL.md step that sends Claude here.>

## <Catalog / Reference body>

<!-- Example shape — a table the skill consults while working. Replace freely. -->

| <Variant> | When to use it | Notes |
|---|---|---|
| `<variant-a>` | <condition> | <gotcha> |
| `<variant-b>` | <condition> | <gotcha> |

## Worked example

<!--
Use a NEUTRAL example domain (Product / Category / Widget / Order). Never real
schemas, org names, internal entities, or absolute paths. Namespaces, base
types, and paths should be <ANGLE_BRACKET> placeholders the adopter fills in.
-->

```text
<Input: ...>
<Output the skill should produce for that input.>
```
