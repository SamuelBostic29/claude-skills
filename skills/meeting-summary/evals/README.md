# Evals — meeting-summary

Run each case in a fresh session with the skill installed, the Microsoft 365
MCP connector connected, and `~/.claude/meeting-summary.local` pointing at a
scratch copy of the notes repo.

## Case 1 — SharePoint recording link, happy path

**Setup:** A transcribed recurring meeting exists on the calendar (e.g. a sprint
review). Its series folder does not yet contain a note for this date.

**Prompt:** Paste the meeting's SharePoint recording URL and ask "summarize this
meeting".

**Expected:**
- [ ] Config gate passes silently (no setup chatter).
- [ ] Calendar event found from the decoded filename; transcript fetched in full.
- [ ] `get_me` called; "My Follow-ups" contains only the current user's items.
- [ ] Meeting note written to `{NOTES_ROOT}\{Series}\{YYYY-MM-DD} {Name}.md`
      matching the template in `references/note-formats.md`.
- [ ] One project doc created/updated per workstream, new entry at the TOP of
      Meeting History; prior entries untouched.
- [ ] Chat output is the four-line report only — no transcript replay.
- [ ] Nothing committed or pushed.

## Case 2 — no transcript available

**Setup:** A calendar event for a meeting that was not transcribed.

**Prompt:** "Summarize yesterday's {meeting name}."

**Expected:**
- [ ] The skill states the transcript is unavailable — it does NOT produce a
      summary from the event body, its own memory, or guesswork.
- [ ] Offers a clearly-marked skeleton note via AskUserQuestion and writes it
      only on an explicit yes.
- [ ] On "no", nothing is written.

## Case 3 — existing note at the target path

**Setup:** Run case 1 once, then run it again for the same meeting.

**Expected:**
- [ ] The skill detects the existing meeting note and asks overwrite/skip
      before writing — it never silently clobbers it.
- [ ] On "skip", project docs are also left unchanged.

## Case 4 (negative) — should not fire / should redirect

**Prompt:** "Summarize this email thread for me" (an Outlook thread, no meeting
reference), or "summarize tomorrow's planning meeting".

**Expected:**
- [ ] The skill does not run its pipeline: no calendar search for the email
      case; for the future meeting it states there is no transcript yet and
      stops.
- [ ] No files are written in either case.
