# Contributing

## Source layout

The packaged source of truth is:

```text
src/imfusion_agent_skills/assets/
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
- **Claude Code** — the body becomes `.claude/rules/*.md`, and `globs` are translated into Claude rule scoping
- **OpenCode** — the body is merged into the managed `AGENTS.md` section, prefixed with the rule name and its scope

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

Authoring constraints, all enforced by `tests/test_assets.py`:

- every frontmatter entry must be a single `key: value` line, with the space after the colon — the packaged parser is deliberately simple and YAML block scalars or lists are not supported;
- rule filenames form a flat namespace, because skills and other rules refer to rules by that name;
- every `@reference` in a body must name a file in `assets/references/`.

Write the rule body in plain markdown and keep it **agent-neutral**. Avoid Cursor-only syntax in rule bodies unless the renderer explicitly handles it.

### How scoping maps onto each agent

Cursor's three activation modes do not exist everywhere, so `renderers.py` makes these trade-offs:

| Source frontmatter | Cursor | Claude Code | OpenCode |
| --- | --- | --- | --- |
| `globs` set, `alwaysApply: false` | attached on matching files | `paths` list, so loaded on matching files | always in context, labelled with its patterns |
| `alwaysApply: true` | always applied | no frontmatter, so always loaded | always in context |
| no `globs`, `alwaysApply: false` | requested by the agent from `description` | no frontmatter, so always loaded | always in context |

Two consequences are worth keeping in mind when writing rules. A description-only rule is cheap in Cursor but costs context in the other two agents, so keep those rules short. And Claude Code only recognises frontmatter that starts at the very first byte of the file, which is why the provenance comment in generated `.claude/rules/*.md` sits below the frontmatter — `tests/test_renderers.py` pins that layout.

### Skills (`assets/skills/*/SKILL.md`)

Skills use the tool-neutral [Agent Skills](https://agentskills.io) format, not Cursor rule syntax. Each skill is a directory containing a `SKILL.md` with frontmatter such as `name` and `description`, followed by the workflow body. The same file is installed unchanged for Cursor, Claude Code, and OpenCode.

The `name` in the frontmatter must match the directory name, and the directory name must be lowercase with single hyphens — OpenCode rejects skills that violate either rule.

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

Lint, format, run the tests, and validate both distribution formats:

```sh
uv run ruff check .
uv run ruff format .
uv run pytest
uv build
uv run twine check dist/*
uv run python .github/scripts/check_assets.py
```

When using a regular Python environment, run the equivalent commands through `python -m`:

```sh
python -m ruff check .
python -m ruff format .
python -m pytest
python -m build
python -m twine check dist/*
python .github/scripts/check_assets.py
```

The code base is tab-indented; `ruff format` is configured accordingly, so let it settle formatting questions. The `ruff` version range is narrow on purpose, because formatting output changes between minor releases and CI checks it.

## Release preparation

Releases are published by `.github/workflows/release.yml`, which builds on a `v*` tag and uploads through PyPI [trusted publishing](https://docs.pypi.org/trusted-publishers/) from the `pypi` environment. That publisher has to be configured once on PyPI before the first release.

Before a release:

1. Update the version in `pyproject.toml`.
2. Run the verification commands above.
3. Push the release commit and wait for CI.
4. Tag the commit as `v<version>` and push the tag; the release workflow verifies that the tag matches the project version before publishing.
