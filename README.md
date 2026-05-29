# ImFusion SDK Agent Kit

This repository contains rules and skills to help external developers create plugins and applications with the ImFusion SDK.

*Rules* are general coding guidelines loaded automatically by the AI agent when relevant files are open.
*Skills* are step-by-step checklists invoked on demand for specific tasks.

## Repository structure

```
cursor/
├── rules/*.mdc          — Cursor rules (source of truth)
└── skills/*/SKILL.md    — skill checklists

claude/
├── rules/*.md           — Claude Code rules (auto-generated)
└── skills/*/SKILL.md    — skill checklists (auto-generated)

AGENTS.md                — OpenCode rules (auto-generated)
```

`cursor/` is the only folder maintained by hand. `claude/` and `AGENTS.md` are generated from it by `scripts/generate_rules.py`.

## Setup

Add this repository as a git submodule in your project and symlink the tool-specific folders:

```sh
# Add as submodule
git submodule add <repo-url> imfusion-agent-kit

# Cursor
ln -s imfusion-agent-kit/cursor .cursor

# Claude Code
ln -s imfusion-agent-kit/claude .claude

# OpenCode
ln -s imfusion-agent-kit/AGENTS.md AGENTS.md
```

After this, all three tools pick up rules and skills automatically with no further configuration.

> **Note:** if your project already has a `.cursor/` or `.claude/` folder, copy the `rules/` and `skills/` subfolders into the existing directory instead of symlinking the top level.

### Cursor workspace (recommended)

For optimal results, use a Cursor workspace that also indexes the ImFusion SDK install folder and the public demos so Cursor can reference them directly.

Create a `your-project.code-workspace` file and open it in Cursor:

```json
{
	"folders": [
		{ "path": "." },
		{ "path": "C:/Program Files/ImFusion/ImFusion Suite" },
		{ "path": "C:/public-demos" }
	],
	"settings": {}
}
```

### Invoking skills

Skills are not loaded automatically — invoke them by referencing the skill file in your prompt, e.g.:

> *"Follow the checklist in `.cursor/skills/create-imfusion-algorithm/SKILL.md` to create a new algorithm."*

For Claude Code use `.claude/skills/…`, for OpenCode use `imfusion-agent-kit/cursor/skills/…`.

## Contributing

The number of skills should be kept as low as possible.

Rules and skills should not duplicate information in the documentation, but focus on implicit knowledge, unexpected behaviour, or repeated errors made by AI agents. LLM-generated skills are generally not useful and can be erroneous or confusing.

**Edit only `cursor/rules/*.mdc` and `cursor/skills/`.** Never edit `claude/` or `AGENTS.md` directly — they are auto-generated.

After changing any rule or skill, regenerate the Claude Code and OpenCode files:

```sh
python3 scripts/generate_rules.py
```

A pre-commit hook does this automatically on every commit. Enable it once per clone:

```sh
git config core.hooksPath .githooks
```
