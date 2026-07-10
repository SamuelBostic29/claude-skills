# Note formats — paths, naming, and markdown templates

Step 7 of `meeting-summary` sends you here. `{NOTES_ROOT}` is the value from
`~/.claude/meeting-summary.local`.

## File layout

Notes are organized **by meeting series, then date**:

```
{NOTES_ROOT}\
  {Series Name}\{YYYY-MM-DD} {Meeting Name}.md   ← one file per occurrence
  Projects\{Project Name}.md                     ← one file per workstream
```

- **Series Name** — the recurring series' subject; for a one-off meeting, the
  meeting's own subject. Strip characters illegal in Windows filenames
  (`\ / : * ? " < > |`) from both folder and file names.
- **Meeting Name** — the occurrence's subject. When it equals the series name
  (the usual case), the file is `{YYYY-MM-DD} {Series Name}.md`.
- Wikilinks (`[[...]]`) reference other files by filename without path or
  extension — keep names stable so links keep resolving.

## Meeting note template

```markdown
# {Meeting Name}

**Date:** {YYYY-MM-DD}
**Time:** {HH:MM} - {HH:MM} {timezone}
**Attendees:** {comma-separated names}

## Discussion

### {Topic 1}
{Concise summary: key points, considerations raised, any debate or alternatives.}

### {Topic 2}
{...}

## Decisions

- {Decision — stated precisely, with who made or confirmed it, plus any conditions}

## Follow-ups

- [ ] {Action item} — {owner, if stated} {deadline, if mentioned}

## My Follow-ups

- [ ] {Action item assigned to or volunteered by the user (per get_me)}

## Projects Referenced

- [[{Project Name}]]

## Previous Meetings Referenced

- [[{YYYY-MM-DD} {Previous Meeting Name}]] — {what was referenced or resolved}
```

Template rules:

- Follow-ups use checkbox syntax `- [ ]` so they're trackable.
- No decisions made → keep the section with "No explicit decisions were made in
  this meeting." Never silently omit it.
- No previous meetings referenced → omit that section entirely.

## Project doc template

**New project** — create `{NOTES_ROOT}\Projects\{Project Name}.md`:

```markdown
# {Project Name}

## Meeting History

### [[{YYYY-MM-DD} {Meeting Name}]]

**Key Points:**
- {Point relevant to this project}

**Decisions:**
- {Decisions from this meeting affecting this project}

**Open Items:**
- [ ] {Follow-ups related to this project}
```

**Returning project** — read the existing file, then insert a new entry at the
**top** of `## Meeting History` (reverse chronological):

```markdown
### [[{YYYY-MM-DD} {Meeting Name}]]

**Key Points:**
- {...}

**Decisions:**
- {...}

**Open Items:**
- [ ] {new items}

**Resolved from Previous:**
- [x] {prior open items this meeting closed out}
```

Update rules:

- Check off (`- [x]`) previously open items resolved in this meeting, in place,
  in the older entry where they live.
- Include "Resolved from Previous" only when something was actually resolved.
- Prior entries are **append-only history** — never rewrite, reorder, or delete
  them.
