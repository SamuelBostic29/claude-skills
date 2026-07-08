#!/usr/bin/env python3
"""Validate every skill in this repo against the catalog's quality bar.

Per skills/<name>/:
  - SKILL.md exists
  - frontmatter (between --- fences) parses as YAML
  - name matches the directory name
  - description is present and non-empty
  - allowed-tools is present
  - evals/README.md exists

Repo-wide:
  - every relative markdown link resolves (http(s)/mailto, pure anchors, and
    <PLACEHOLDER> targets are skipped)

template/ is exempt from the per-skill rules — it intentionally ships
placeholders — but its links are still checked.

Exit 0 = clean. Exit 1 = violations, one per line.
"""

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
FRONTMATTER_RE = re.compile(r"^(?:<!--.*?-->\s*)?---\s*\n(.*?)\n---\s*(?:\n|$)", re.DOTALL)


def check_skill(skill_dir: Path) -> list[str]:
    errs = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return [f"{skill_dir.name}: missing SKILL.md"]
    match = FRONTMATTER_RE.match(skill_md.read_text(encoding="utf-8"))
    if not match:
        errs.append(f"{skill_dir.name}: SKILL.md has no frontmatter fences")
    else:
        frontmatter = None
        try:
            frontmatter = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError as exc:
            errs.append(f"{skill_dir.name}: frontmatter is not valid YAML ({exc})")
        if frontmatter is not None:
            if frontmatter.get("name") != skill_dir.name:
                errs.append(
                    f"{skill_dir.name}: frontmatter name {frontmatter.get('name')!r} != directory name"
                )
            if not str(frontmatter.get("description") or "").strip():
                errs.append(f"{skill_dir.name}: description missing or empty")
            if "allowed-tools" not in frontmatter:
                errs.append(f"{skill_dir.name}: allowed-tools missing")
    if not (skill_dir / "evals" / "README.md").is_file():
        errs.append(f"{skill_dir.name}: missing evals/README.md")
    return errs


def check_links() -> list[str]:
    errs = []
    files = sorted(ROOT.glob("*.md"))
    for sub in ("skills", "template"):
        files += sorted((ROOT / sub).rglob("*.md"))
    for md in files:
        for raw in LINK_RE.findall(md.read_text(encoding="utf-8")):
            target = raw.split("#", 1)[0]
            if not target or "<" in target or target.startswith(("http://", "https://", "mailto:")):
                continue
            if not (md.parent / target).exists():
                errs.append(f"{md.relative_to(ROOT)}: broken link -> {raw}")
    return errs


def main() -> int:
    skill_dirs = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir())
    errs = [e for d in skill_dirs for e in check_skill(d)] + check_links()
    if errs:
        print(f"validate-skills: {len(errs)} violation(s)")
        for err in errs:
            print(f"  - {err}")
        return 1
    print(f"validate-skills: OK — {len(skill_dirs)} skills validated, all markdown links resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
