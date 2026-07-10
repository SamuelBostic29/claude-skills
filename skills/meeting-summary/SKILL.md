---
name: meeting-summary
version: 1.0.0
description: |
  Use when the user provides a meeting reference — a SharePoint recording URL,
  a Teams meeting/join link, or a meeting named by title or date — and wants it
  summarized, or asks to "summarize the meeting", extract decisions, or pull
  action items from a recorded meeting. Fetches the calendar event and
  transcript via the Microsoft 365 MCP tools and writes structured markdown
  notes (one meeting note plus per-project docs) into the meetings notes repo,
  organized by meeting series then date. Transcript-grounded only — never
  summarizes a meeting it could not fetch a transcript for.
allowed-tools:
  - Read
  - Write
  - Glob
  - AskUserQuestion
  - mcp__claude_ai_Microsoft_365__outlook_calendar_search
  - mcp__claude_ai_Microsoft_365__read_resource
  - mcp__claude_ai_Microsoft_365__get_me
---

# Meeting Summary: turn a recorded Teams meeting into structured notes

You are turning one recorded Teams meeting into durable markdown notes: a meeting
note filed under its series folder, plus a per-project doc for each workstream it
touched. Everything you write must be grounded in the fetched transcript — the
cardinal failure here is **fabricating a summary** when the transcript is missing
or partial, or **silently overwriting** a note that already exists. If you can't
fetch the transcript, say so and stop; if the note exists, ask.

## First action on every invocation — the config gate

Before replying or asking anything, resolve the notes root, silently:

1. Read `~/.claude/meeting-summary.local` (i.e. `$HOME/.claude/meeting-summary.local`).
2. A line `NOTES_ROOT="<path>"` with a real existing directory → proceed.
3. File missing, value empty, or still a `<...>` placeholder → run **Setup**, then stop.

**Setup:** Write this template to `~/.claude/meeting-summary.local` (never clobber
a real value), tell the user to fill in the path to their clone of the meetings
notes repo and save, then stop:

```
# meeting-summary config — per-user, never committed.
# Set NOTES_ROOT to your local clone of the meetings notes repo.
NOTES_ROOT="<PATH_TO_YOUR_MEETINGS_NOTES_REPO>"
```

## When to use this skill

- User pastes a SharePoint recording link (`https://...sharepoint.com/.../Recordings/...`)
- User pastes a Teams meeting or join link
- User asks to summarize a meeting by name or date ("summarize this morning's sprint review")
- User wants decisions or action items extracted from a recorded meeting

## When NOT to use this skill

- **Summarizing an email thread, chat, or document** — that's ad-hoc summarization, not this skill; no calendar event or transcript is involved.
- **Live/future meetings** — there is no transcript yet; say so and stop.
- **Editing existing notes by hand** ("fix the attendee list in Tuesday's note") — just edit the file directly.

## Steps

1. **Identify the meeting.** Locate the calendar event with
   `outlook_calendar_search`:
   - *SharePoint recording link:* URL-decode the filename; extract the meeting
     name (text before the `-YYYYMMDD_HHMMSS-Meeting Recording.mp4` suffix) and
     the date. Search by name, narrow by date.
   - *Teams join link:* search by any keywords in the link, or list events near
     the implied date and match on the event's `onlineMeeting` join URL.
   - *Name/date:* search directly.
   Multiple plausible matches → present them via AskUserQuestion and stop until
   answered. Zero matches → report what you searched and stop.

2. **Read the calendar event.** `read_resource` with `calendar:///events/{eventId}`.
   Record: subject, series name (recurring-series subject; for a one-off, the
   subject itself), start/end + timezone, attendees, `meetingTranscriptUrl`, and
   any agenda in the body.

3. **Fetch the transcript.** `read_resource` with the event's
   `meetingTranscriptUrl` verbatim (format `meeting-transcript:///events/{token}`).
   For a recurring series, append `?start={iso}&end={iso}` to scope to the
   occurrence. Delivered in chunks → fetch all chunks before summarizing.
   **No transcript → do not summarize.** Tell the user and offer a skeleton note
   (metadata only, clearly marked as untranscribed) via AskUserQuestion; only
   write it if they say yes.

4. **Resolve the user's identity.** Call `get_me` once — the returned
   name/email defines whose action items go under "My Follow-ups". Never assume
   an identity from the notes or config.

5. **Gather prior context.** Glob `{NOTES_ROOT}/Projects/*.md` and the meeting's
   series folder `{NOTES_ROOT}/{Series Name}/*.md`; read the docs whose names
   match projects, products, or prior meetings referenced in the transcript.
   Use them to separate what's NEW from what was already decided, and to spot
   prior open items this meeting resolved.

6. **Analyze the transcript.** Extract: discussion topics (grouped, each with a
   concise summary), decisions (stated precisely, with who confirmed them),
   team follow-ups (owner + deadline when stated), the user's own follow-ups
   (explicit assignments and clear volunteerings), the distinct
   projects/workstreams discussed, and any callbacks to prior meetings.

7. **Write the notes.** Read `references/note-formats.md` for the exact file
   paths, naming, and markdown templates, then write the meeting note and
   create/update one project doc per project identified. If the meeting note
   already exists at the target path, ask (overwrite / skip) via
   AskUserQuestion before touching it. Project docs are append-only history —
   add the new entry at the top of Meeting History, check off resolved items,
   never rewrite prior entries.

8. **Report and stop.** Use the Output format below. Do not commit or push the
   notes repo — writing the files is where this skill ends.

## Output format

```
Meeting note: {NOTES_ROOT}\{Series Name}\{YYYY-MM-DD} {Meeting Name}.md
Project docs: {created: X, updated: Y — names}
Summary: {topics} topics, {decisions} decisions, {follow-ups} follow-ups ({n} yours)
Resolved from previous meetings: {list, or "none"}
```

## Rules

### What to do

- **Ground every claim in the transcript.** Decisions verbatim-precise with the
  decider named; follow-ups only when actually assigned or volunteered.
- **Full transcript, always.** Never truncate or sample a long transcript; fetch
  every chunk first.
- **Ask at every fork.** Ambiguous meeting match, recurring occurrence, existing
  note at the target path, unclear project grouping → AskUserQuestion, never guess.
- **Identity comes from `get_me`,** paths come from the config file. Nothing
  personal is hardcoded in this skill.

### What NOT to do

- **NEVER fabricate a summary without a transcript.** No transcript means a
  clearly-marked skeleton (with consent) or nothing.
- **NEVER overwrite an existing meeting note unprompted,** and never rewrite or
  delete prior entries in a project doc.
- **NEVER commit or push** the notes repo — file writes only.
- **Don't paraphrase decisions loosely** — a softened decision is a wrong decision.

### Format discipline

- The deliverable is the note files plus the four-line report. No transcript
  replay in chat, no narrating each step, no recap of the note contents beyond
  the counts.
