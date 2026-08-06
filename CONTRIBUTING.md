# Contributing

## Source layout

The packaged source of truth is:

```text
src/imfusion_sdk_agent_kit/assets/
├── rules/       # Cursor .mdc source rules
├── skills/      # tool-neutral Agent Skills
└── references/  # templates referenced by rules
```

Do not add generated Cursor, Claude Code, or OpenCode output to the repository. The CLI renders agent-specific files from these packaged assets.

Keep the number of skills low. Rules and skills should focus on implicit knowledge, unexpected SDK behavior, and repeated agent errors rather than duplicating public documentation.

## Authoring formats

### Rules (`assets/rules/*.mdc`)

Rules are authored in [Cursor rule](https://cursor.com/docs/context/rules) format (`.mdc` with YAML frontmatter). The CLI uses these files as the canonical source for all supported agents:

- **Cursor** — copied unchanged to `.cursor/rules/`
- **Claude Code** — frontmatter is translated into Claude rule scoping; the body becomes `.claude/rules/*.md`
- **OpenCode** — only the markdown body is merged into the managed `AGENTS.md` section

Use this frontmatter shape:

```yaml
---
description: Short summary shown in the agent UI
globs: **/*Algorithm.h,**/*Algorithm.cpp
alwaysApply: false
---
```

- `description` — required for discoverability in Cursor
- `globs` — comma-separated path patterns; omit or set `alwaysApply: true` for workspace-wide rules
- `alwaysApply` — `true` or `false`

Write the rule body in plain markdown and keep it **agent-neutral**. Avoid Cursor-only syntax in rule bodies unless the renderer explicitly handles it. 

### Skills (`assets/skills/*/SKILL.md`)

Skills use the tool-neutral [Agent Skills](https://agentskills.io) format, not Cursor rule syntax. Each skill is a directory containing a `SKILL.md` with frontmatter such as `name` and `description`, followed by the workflow body. The same file is installed unchanged for Cursor, Claude Code, and OpenCode.

### References (`assets/references/`)

Static templates and supporting files referenced from rules or skills. Prefer plain paths or prose over agent-specific `@` references unless you also update the renderer transformations in `renderers.py`.

## Development setup

With uv:

```sh
uv sync --extra dev
```

Without uv:

```sh
python -m pip install -e ".[dev]"
```

## Verification

Run the tests and validate both distribution formats:

```sh
uv run pytest
uv build
uv run twine check dist/*
```

When using a regular Python environment, run the equivalent commands through `python -m`:

```sh
python -m pytest
python -m build
python -m twine check dist/*
```

## Release preparation

Before a release:

1. Update the version in `pyproject.toml`.
2. Run the complete test suite.
3. Build from a clean checkout.
4. Inspect and validate the wheel and source distribution.
5. Publish through the project's trusted PyPI release workflow once configured.
