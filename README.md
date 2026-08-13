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

Until the first PyPI release, install straight from the repository instead:

```sh
uv tool install git+https://github.com/ImFusionGmbH/ImFusionSDK-Agent-Kit
```

## Install into a project

Run the command from the root of your ImFusion SDK project:

```sh
imfusion-sdk-agent-kit init
```

To run it once without installing the CLI permanently, use `uvx imfusion-sdk-agent-kit init`.

Without `--agent`, the command detects which agents to install for. If `.imfusion-sdk-agent-kit/manifest.json` exists it wins outright, so re-running `init` refreshes exactly what is already installed. Otherwise the command combines two signals: agent files in the project (`.cursor/`, `.claude/`, `CLAUDE.md`, `.opencode/`, or an `AGENTS.md` that already contains this kit's section) and the environment of the agent running the command, which covers a project that has no agent files yet.

A bare `AGENTS.md` is deliberately ignored, because several tools read that file and its presence identifies none of them.

If nothing is detected the command exits without writing anything and asks you to pass `--agent`. Name the agents explicitly whenever you want to control the result:

```sh
# Cursor
imfusion-sdk-agent-kit init --agent cursor

# Claude Code
imfusion-sdk-agent-kit init --agent claude

# OpenCode
imfusion-sdk-agent-kit init --agent opencode

# A project other than the current directory
imfusion-sdk-agent-kit init path/to/project --agent cursor,claude
```

The command installs native project files:

- Cursor: `.cursor/rules/` and `.cursor/skills/`
- Claude Code: `.claude/rules/` and `.claude/skills/`
- OpenCode: `.opencode/skills/`, `.opencode/references/`, and a managed section in `AGENTS.md`

The rules directories also receive the C++ template files that some rules reference, so `.cursor/rules/` and `.claude/rules/` contain a few `.h` and `.cpp` files next to the rules themselves. OpenCode keeps those in `.opencode/references/`.

Because the three tools scope guidance differently, the same source rules behave slightly differently once installed:

- Cursor and Claude Code attach file-scoped rules only when the agent touches matching files.
- OpenCode has no scoped-rule mechanism, so all rules live in the `AGENTS.md` section and are always in context. Each one is labelled with its name and the file patterns it applies to.

Use `--dry-run` to inspect changes. Use `--force` only when you intend to replace files that conflict with kit-managed paths.

## Safe updates

The installer merges into existing agent directories. It records installed file hashes in `.imfusion-sdk-agent-kit/manifest.json` and follows these rules on later runs:

- unchanged kit-managed files are updated to the installed package version;
- unrelated project files and existing `AGENTS.md` content are preserved;
- user-modified or unknown same-named files stop the installation before any changes are written;
- `--force` explicitly replaces those conflicts;
- managed files that the kit no longer ships are removed if unchanged, and kept but no longer managed if you edited them;
- files keep the line endings they already had, so an update does not rewrite every line of a CRLF checkout.

To update:

```sh
uv tool upgrade imfusion-sdk-agent-kit
imfusion-sdk-agent-kit init
```

The second command needs no `--agent`, because the manifest already records which agents the project uses.

With a regular Python environment, replace `uv tool upgrade` with `python -m pip install --upgrade imfusion-sdk-agent-kit`.

## Remove installed guidance

There is no automatic uninstall command in the initial release. Remove the installed ImFusion files listed in `.imfusion-sdk-agent-kit/manifest.json`, then remove `.imfusion-sdk-agent-kit/`. For OpenCode, remove only the section between:

```text
<!-- imfusion-sdk-agent-kit:start -->
<!-- imfusion-sdk-agent-kit:end -->
```

Do not remove an entire `.cursor`, `.claude`, `.opencode`, or `AGENTS.md` path if it also contains project-owned content.

Leaving an agent out of `--agent` does not uninstall it: the installer only manages the agents you pass on that run, so files for other agents stay untouched. `AGENTS.md` itself is never deleted — when a managed section becomes obsolete, only the section is stripped out.

## Give the agent access to the SDK and demos

The installed rules and skills describe ImFusion APIs, but they do not contain the SDK headers or complete example implementations. Several rules and skills tell the agent to consult working examples, so make these available in every project where you install the kit:

1. Your local ImFusion SDK installation.
2. The [ImFusion public demos](https://github.com/ImFusionGmbH/public-demos) checked out at the tag matching your SDK version, such as `imfusion-sdk-v4.4`.

With Claude Code, add both directories to the session (for example with `/add-dir`) or keep the demos checkout inside the project tree. With OpenCode, run the agent from a directory that contains both, or point it at the checkout when you ask for an example. In Cursor, use a multi-root workspace as described below.

### Cursor workspace recommendation

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

### Optional: make the SDK documentation available

Headers and demos cover most coding tasks, but conceptual guides and fuller API reference live in the official documentation at [docs.imfusion.com](https://docs.imfusion.com) (C++ and Python SDK developer docs).

In Cursor, add that site under **Settings → Indexing & Docs → Docs** so the agent can look up topics the installed rules and skills deliberately do not duplicate. Claude Code and OpenCode can reach the same pages with their web fetch tools when those are enabled.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, content guidelines, testing, and release preparation.

## License

Licensed under the [MIT License](LICENSE).
