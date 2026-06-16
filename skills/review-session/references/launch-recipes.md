# Launch recipes — spawning the detached interactive reviewer

Step 5 of `review-session` sends you here. Pick the recipe for the current OS,
substitute `REPO` (repo root), `BRIEF` (absolute brief path), and `PROMPT`, then
launch. Every recipe must **return immediately** (detached) and open a window the
user can type into. `claude "<prompt>"` starts an interactive session by default —
do **not** add `-p`.

**Quoting is the #1 failure mode — pass `PROMPT` as a single argument.** If the
launcher word-splits it, `claude` receives only the first token (`Read`) and
silently does nothing useful. Keep `BRIEF` and the temp filename free of spaces and
quotes, and keep `PROMPT` free of apostrophes and quotes — the macOS/Linux recipes
nest it inside single- and double-quotes, so one stray `'` breaks the spawn. After
launching, confirm the window actually *started the review* — not merely that a
window opened.

`PROMPT` — the one canonical string; use it verbatim in every recipe below:

```
Read the review brief at BRIEF and carry out the cold code review it describes. You are seeing this code for the first time — review it on its own merits.
```

## Windows (verified)

Launch with PowerShell `Start-Process`, passing the prompt as **one quoted
argument** — this is the form proven to work in practice:

```powershell
$prompt = "Read the review brief at BRIEF and carry out the cold code review it describes. You are seeing this code for the first time — review it on its own merits."
Start-Process -FilePath claude.exe -WorkingDirectory 'REPO' -ArgumentList ('"' + $prompt + '"')
```

Use the full path to `claude.exe` if it isn't on PATH. On Win11 this opens in your
default terminal (usually Windows Terminal). For an explicit Windows Terminal
window with tabs:

```powershell
Start-Process wt.exe -ArgumentList @('-d','REPO','claude.exe', ('"' + $prompt + '"'))
```

**Avoid** the bare-shell form `wt.exe -d "REPO" claude "PROMPT"` — its commandline
parsing word-splits the prompt and `claude` receives only the first token.

## macOS

Terminal.app via AppleScript (opens a new window, returns immediately):

```bash
osascript -e 'tell app "Terminal" to do script "cd \"REPO\" && claude \"PROMPT\""'
```

iTerm2 users: substitute the equivalent `osascript` for `iTerm`.

## Linux

Use the desktop's terminal, and **fully detach** so the calling Bash tool can't block
on an inherited stdout pipe — `setsid … </dev/null >/dev/null 2>&1 &`, not a bare `&`:

```bash
setsid x-terminal-emulator -e bash -c 'cd "REPO" && claude "PROMPT"; exec bash' </dev/null >/dev/null 2>&1 &
# gnome-terminal: setsid gnome-terminal --working-directory="REPO" -- bash -c 'claude "PROMPT"; exec bash' </dev/null >/dev/null 2>&1 &
# konsole:        setsid konsole --workdir "REPO" -e bash -c 'claude "PROMPT"; exec bash' </dev/null >/dev/null 2>&1 &
```

## Headless / no GUI terminal (SSH, container, CI shell)

**Detect headless deterministically (don't guess):**
- **Linux:** GUI only if `$DISPLAY` or `$WAYLAND_DISPLAY` is set *and* neither `$SSH_CONNECTION` nor `$CI` is set.
- **Windows:** GUI if `wt.exe` resolves or a default terminal exists; treat a bare SSH/CI shell as headless.
- **macOS:** effectively always GUI (unless `$CI`).

When headless: there is no window to open. Do **not** silently fall back to `-p` —
that breaks the interactivity invariant. Instead, **print the exact command** for the
user to run in their own terminal, and stop:

```bash
cd "REPO" && claude "PROMPT"
```

If the host multiplexes terminals, a tmux window is a valid interactive target:

```bash
tmux new-window -c "REPO" "claude 'PROMPT'"
```

## Options worth knowing

- **`--append-system-prompt-file <path>`** — enforce the cold-reviewer stance at the
  system-prompt level instead of (or in addition to) the brief. Useful if you want
  the framing to persist across the whole review, not just the first turn.
- **`--bare`** — a maximally-isolated reviewer: skips hooks, plugins, auto-memory,
  and CLAUDE.md auto-discovery. Use only if you want the review uninfluenced by repo
  conventions; the default (normal session) is usually better, since repo `CLAUDE.md`
  rules make the review sharper.
- **`--model` / `--effort`** — bump the reviewer to a stronger model or higher effort
  for a deeper pass.
