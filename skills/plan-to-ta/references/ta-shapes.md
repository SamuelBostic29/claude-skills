# TA shapes — the four sizes, their conventions, and Jira markup

## Contents
- Choosing a shape
- Shape 1: Micro
- Shape 2: Layer-walk
- Shape 3: Contract
- Shape 4: Full-design
- Conventions that apply to every shape
- Markdown → Jira wiki markup

## Choosing a shape

Match the *plan's* scope, not its length — a verbose plan for a small change still gets a small TA.

| Plan looks like | Shape |
| --- | --- |
| One mechanism, a bug fix, ≤1 phase | Micro |
| A few phases inside one service, no schema/contract churn | Layer-walk |
| Field additions, import/API payload changes, validation rules | Contract |
| New capability across DB + endpoints + logic (± a paired FE side) | Full-design |

## Shape 1: Micro

`**TA**` then 1–3 sentences naming the mechanism. No headers, no tables.

```markdown
**TA**

Wrap the whole form in a disabled fieldset element — no clickable buttons are
expected in read-only mode.
```

## Shape 2: Layer-walk

`### Technical Analysis`, intent sentence, then a short block per architectural layer the change touches — and an explicit "nothing to change" line for layers a reader would expect to move.

```markdown
### Technical Analysis

<What needs to happen and the approach, 1–2 sentences.>

**Endpoints**
Add an optional query param to <endpoint>; pass it through to <downstream call>.

**Business logic**
<Method> forwards the param; no branching changes.

**DTOs**
No DTO changes — <reason, e.g. the property is dynamic>.
```

Per-file bullets are an equally valid layer-walk when the change is config-ish:

```markdown
### Technical Analysis

- `<Service>.cs`: <change>. Keep <thing> on <method> since <reason>.
- `<Config>.cs` + `<IConfig>.cs`: add <ENV_VAR>.
- `launchSettings.json`: add the env var.
```

## Shape 3: Contract

For field/import/API-contract work. Field tables, payload examples, then edge cases as bold-term + one-line resolution pairs.

```markdown
### Technical Analysis

<Why these fields / this naming, 1–2 sentences.>

| Field | C# property | JSON key | Type | Validation |
| --- | --- | --- | --- | --- |
| <name> | `<Property>` | `<jsonKey>` | `<type>` | <range/regex> |

#### Payload example
```json
{ "<jsonKey>": <value> }
```

#### Edge cases

**<Field omitted on create>**
Defaults to <value>.

**<Invalid value>**
Reject the field with a warning; keep existing values.
```

## Shape 4: Full-design

For large features. Sections ordered by architecture; a Current Architecture opener when the reader needs it; a Non-Obvious Considerations closer for the traps.

```markdown
### Technical Analysis

## Current Architecture

<How the relevant piece works today — tables, constraints, merge/priority rules.>

## 1. Database Changes

<Migrations, constraints, indexes. Or "No new tables or columns are needed.">

## 2. Endpoint Changes

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `<route>` | <purpose> |

<Which existing endpoints change, and — explicitly — which don't.>

## 3. DTO Changes

<New/changed DTOs, or "No changes to <Dto> are needed" with the reason.>

## 4. Non-Obvious Considerations

### <Trap or interaction>
<Why it works or what must be watched — e.g. "the publish flow copies these
rows generically, so no code change is needed.">
```

## Conventions that apply to every shape

- Intent opener before mechanics (except micro, where the sentence *is* the mechanism).
- Real identifiers, spot-verified against the code when the repo is local.
- Negative space stated explicitly per area ("Modified endpoints: none").
- Tables over prose for enumerable facts.
- No execution machinery, no AC tags, no counts, no ticket keys in prose.

## Markdown → Jira wiki markup

Jira Data Center descriptions render wiki markup, not markdown. Convert on push:

| Markdown | Jira wiki markup |
| --- | --- |
| `### Heading` / `## Heading` | `h3. Heading` / `h2. Heading` |
| `**bold**` | `*bold*` |
| `` `code` `` | `{{code}}` |
| ```` ```json … ``` ```` | `{code:json} … {code}` |
| `\| a \| b \|` header row | `\|\|a\|\|b\|\|` then `\|cell\|cell\|` rows |
| `- item` | `* item` |
| `1. item` | `# item` |
| `[text] (url)` — md link, no space | `[text\|url]` |
| `---` | `----` |

Drop the trailing status line (`Shape: … · Target: …`) — it's chat-only, never part of the ticket.
