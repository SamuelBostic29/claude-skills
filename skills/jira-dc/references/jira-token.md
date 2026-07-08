# Jira token — resolution & secrecy (single source)

Only the `jira-dc` skill resolves the per-user PAT — it is the single resolver. Anything else
that needs Jira data defers the whole fetch to this skill and never touches the token itself.
**This file is the one owner of that resolve+extract logic — cite it, don't re-inline it.**
(Re-inlined copies drift; that is how a token model ends up contradicting itself across files.)
The lone sanctioned re-inline is the skill's first-action token gate, which must run before any
reference can be read; it keeps a copy in lockstep with this file.

## Resolve the token file — fresh, every call

A provisioned **repo** copy wins; otherwise your **home** copy (which works outside any repo).
*Provisioned* means the repo git-ignores `.claude/jira-token.local` — the same `git check-ignore`
test the skill's Setup uses to choose its write target, so read and write resolve to the same
file. Resolve it silently — never narrate the path or repo:

```bash
R="$(git rev-parse --show-toplevel 2>/dev/null)"
if [ -n "$R" ] && git -C "$R" check-ignore -q "$R/.claude/jira-token.local" 2>/dev/null && [ -s "$R/.claude/jira-token.local" ]; then
  TOKEN_FILE="$R/.claude/jira-token.local"      # provisioned (git-ignored) repo copy, with a token in it
else
  TOKEN_FILE="$HOME/.claude/jira-token.local"   # home default — works outside any repo
fi
```

`git rev-parse` returning nothing outside a repo is expected — fall back to home, never fail. The
trailing `-s` is the read-only addition (there must be a token to read); Setup uses the same
`git check-ignore` test without it, since at first write the file does not exist yet.

**Presence gate (read flows):** extract the value (as `auth_cfg` does) and test it — a non-empty value
that isn't the `<…>` placeholder is `set`, else `unset`; only `set`/`unset` may reach the transcript,
never the token. `unset` → don't call curl; tell the user once to run the skill's Setup.

## Feed it to curl — never argv, never printed

```bash
# the file is JIRA_TOKEN="…" (with # comments); auth_cfg extracts the value, tolerating a legacy bare token
auth_cfg() { local t; t="$(sed -n '/^[[:space:]]*#/d;s/.*"\([^"]*\)".*/\1/p' "$TOKEN_FILE" | head -1)"; [ -z "$t" ] && t="$(grep -vE '^[[:space:]]*(#|$)' "$TOKEN_FILE" | head -1)"; printf 'header = "Authorization: Bearer %s"\n' "$(printf %s "$t" | tr -d '\r\n')"; }
# read:  auth_cfg | curl -sS -K - ...
```

- The token crosses **only** on stdin via the `-K -` `header = "…"` directive — never `-H`/argv,
  never a command log.
- Strip CR/LF on read (a Windows newline → `Bearer …\r` → silent 401).
- **Never** echo, print, or return it; no `curl -v`, no `set -x` while it's in scope.

(First-time *write* of the token — gitignore-before-write, no-echo capture, `/myself` confirmation —
is the skill's **Setup** section, a separate concern from reading it here.)
