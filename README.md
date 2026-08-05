# ImFusion SDK Agent Kit

Install project-level rules and skills that help AI coding agents build plugins and applications based on the ImFusion SDK.

Rules provide focused coding guidance when relevant files are open. Skills provide reusable workflows for tasks such as creating a plugin, configuring CMake, and working with image data.

## Install

The recommended installation uses [uv](https://docs.astral.sh/uv/getting-started/installation/) to install the CLI in an isolated environment:

```sh
uv tool install imfusion-sdk-agent-kit
```

If uv is not available, install it with standard pip:

```sh
python -m pip install imfusion-sdk-agent-kit
```

Python 3.10 or newer is required.

## Install into a project

Run the command from the root of your ImFusion SDK project:

```sh
imfusion-sdk-agent-kit init --agent cursor,claude
```

Choose one or more comma-separated agents:

```sh
# Cursor
imfusion-sdk-agent-kit init --agent cursor

# Claude Code
imfusion-sdk-agent-kit init --agent claude

# OpenCode
imfusion-sdk-agent-kit init --agent opencode

# A project other than the current directory
imfusion-sdk-agent-kit init --agent cursor,claude --project path/to/project
```

The command installs native project files:

- Cursor: `.cursor/rules/` and `.cursor/skills/`
- Claude Code: `.claude/rules/` and `.claude/skills/`
- OpenCode: `.opencode/skills/`, `.opencode/references/`, and a managed section in `AGENTS.md`

Use `--dry-run` to inspect changes. Use `--force` only when you intend to replace files that conflict with kit-managed paths.

## Safe updates

The installer merges into existing agent directories. It records installed file hashes in `.imfusion-sdk-agent-kit/manifest.json` and follows these rules on later runs:

- unchanged kit-managed files are updated to the installed package version;
- unrelated project files and existing `AGENTS.md` content are preserved;
- user-modified or unknown same-named files stop the installation before any changes are written;
- `--force` explicitly replaces those conflicts;
- obsolete, unchanged managed files are removed, while modified obsolete files are kept and no longer managed.

To update:

```sh
uv tool upgrade imfusion-sdk-agent-kit
imfusion-sdk-agent-kit init --agent cursor,claude
```

With a regular Python environment, replace `uv tool upgrade` with `python -m pip install --upgrade imfusion-sdk-agent-kit`.

## Remove installed guidance

There is no automatic uninstall command in the initial release. Remove the installed ImFusion files listed in `.imfusion-sdk-agent-kit/manifest.json`, then remove `.imfusion-sdk-agent-kit/`. For OpenCode, remove only the section between:

```text
<!-- imfusion-sdk-agent-kit:start -->
<!-- imfusion-sdk-agent-kit:end -->
```

Do not remove an entire `.cursor`, `.claude`, `.opencode`, or `AGENTS.md` path if it also contains project-owned content.

## Cursor workspace recommendation

The installed rules and skills describe ImFusion APIs, but they do not contain the SDK headers or complete example implementations. For better results, let Cursor index all three relevant codebases:

1. Your project.
2. Your local ImFusion SDK installation.
3. The [ImFusion public demos](https://github.com/ImFusionGmbH/public-demos) checked out at the tag matching your SDK version, such as `imfusion-sdk-v4.4`.

Create a multi-root workspace file such as `your-project.code-workspace` in your project root:

```json
{
	"folders": [
		{ "name": "Project", "path": "." },
		{
			"name": "ImFusion SDK",
			"path": "C:/Program Files/ImFusion/ImFusion Suite"
		},
		{ "name": "ImFusion public demos", "path": "C:/Dev/public-demos" }
	],
	"settings": {}
}
```

Adjust the paths for your system, then open the `.code-workspace` file in Cursor.
Cursor can then inspect SDK declarations and matching working examples when applying the installed guidance.
The SDK and demos remain external dependencies; they are not copied into your project.

### Optional: index SDK documentation

Headers and demos cover most coding tasks, but conceptual guides and fuller API reference live in the official documentation at [docs.imfusion.com](https://docs.imfusion.com) (C++ and Python SDK developer docs).

In Cursor, add that site under **Settings → Indexing & Docs → Docs** so the agent can look up topics the installed rules and skills deliberately do not duplicate.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, content guidelines, testing, and release preparation.

## License

Licensed under the [Apache License 2.0](LICENSE).
