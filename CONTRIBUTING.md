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
