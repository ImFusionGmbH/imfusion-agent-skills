#!/usr/bin/env python3
"""
Generate Claude Code and OpenCode files from Cursor .mdc sources.

Source (human-maintained):
  cursor/rules/*.mdc          — rules with Cursor frontmatter
  cursor/skills/*/SKILL.md    — skill checklists

Generated (do not edit directly):
  claude/rules/*.md           — rules with Claude Code `paths:` frontmatter
  claude/skills/*/SKILL.md    — copies of skill files
  AGENTS.md                   — concatenated rules for OpenCode

Run manually:
  python3 scripts/generate_rules.py

Or automatically on every commit via the pre-commit hook:
  git config core.hooksPath .githooks
"""

import re
import shutil
import sys
from pathlib import Path

CURSOR_RULES_DIR = Path("cursor/rules")
CURSOR_SKILLS_DIR = Path("cursor/skills")
CLAUDE_RULES_DIR = Path("claude/rules")
CLAUDE_SKILLS_DIR = Path("claude/skills")
AGENTS_FILE = Path("AGENTS.md")


def parse_mdc(path: Path) -> tuple[dict, str]:
    """Return (frontmatter_dict, body) parsed from a .mdc file."""
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n?---\n?(.*)", text, re.DOTALL)
    if not match:
        return {}, text.strip()

    fm: dict = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip()

    return fm, match.group(2).strip()


def to_claude_md(fm: dict, body: str, source: Path) -> str:
    """Build Claude Code .md content from .mdc frontmatter and body."""
    always_apply = fm.get("alwaysApply", "false").lower() == "true"
    globs_str = fm.get("globs", "").strip()
    paths = [g.strip() for g in globs_str.split(",") if g.strip()]

    header = f"<!-- Auto-generated from {source} — do not edit directly -->\n\n"

    if always_apply or not paths:
        return header + body

    paths_block = "\n".join(f'  - "{p}"' for p in paths)
    return f"{header}---\npaths:\n{paths_block}\n---\n\n{body}"


def generate_rules() -> list[str]:
    """Generate .claude/rules/*.md and return rule bodies for AGENTS.md."""
    CLAUDE_RULES_DIR.mkdir(parents=True, exist_ok=True)

    mdc_files = sorted(CURSOR_RULES_DIR.glob("*.mdc"))
    if not mdc_files:
        print(f"No .mdc files found in {CURSOR_RULES_DIR}/", file=sys.stderr)
        sys.exit(1)

    agent_bodies: list[str] = []
    for mdc_file in mdc_files:
        fm, body = parse_mdc(mdc_file)

        out_path = CLAUDE_RULES_DIR / f"{mdc_file.stem}.md"
        out_path.write_text(to_claude_md(fm, body, mdc_file), encoding="utf-8")
        print(f"  {out_path}")

        agent_bodies.append(body)

    return agent_bodies


def copy_skills() -> None:
    """Copy .cursor/skills/ to .claude/skills/."""
    if CLAUDE_SKILLS_DIR.exists():
        shutil.rmtree(CLAUDE_SKILLS_DIR)

    for src in sorted(CURSOR_SKILLS_DIR.rglob("*.md")):
        if not src.is_file():
            continue
        dest = CLAUDE_SKILLS_DIR / src.relative_to(CURSOR_SKILLS_DIR)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        print(f"  {dest}")


def generate_agents_md(rule_bodies: list[str]) -> None:
    """Generate AGENTS.md for OpenCode from rule bodies."""
    content = (
        "<!-- Auto-generated from cursor/rules/*.mdc — do not edit directly -->\n\n"
        + "\n\n---\n\n".join(rule_bodies)
        + "\n"
    )
    AGENTS_FILE.write_text(content, encoding="utf-8")
    print(f"  {AGENTS_FILE}")


def main() -> None:
    print("Generating rules:")
    rule_bodies = generate_rules()

    print("Copying skills:")
    copy_skills()

    print("Generating AGENTS.md:")
    generate_agents_md(rule_bodies)

    print("Done.")


if __name__ == "__main__":
    main()
