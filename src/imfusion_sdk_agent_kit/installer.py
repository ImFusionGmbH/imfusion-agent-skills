"""Safely install rendered guidance into an existing project."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from . import __version__
from .renderers import AGENTS_END, AGENTS_START, SUPPORTED_AGENTS, render_agents

STATE_DIRECTORY = ".imfusion-sdk-agent-kit"
MANIFEST_PATH = Path(STATE_DIRECTORY) / "manifest.json"
MANIFEST_SCHEMA = 1

# Project files that indicate an agent is configured for a project.
AGENT_MARKERS: dict[str, tuple[str, ...]] = {
	"cursor": (".cursor",),
	"claude": (".claude", "CLAUDE.md"),
	"opencode": (".opencode",),
}

# Variables each agent exports into the shells it runs, which identify the agent driving
# the current invocation even in a project that has no agent files yet.
AGENT_ENVIRONMENT: dict[str, tuple[str, ...]] = {
	"cursor": ("CURSOR_AGENT",),
	"claude": ("CLAUDECODE",),
	"opencode": ("OPENCODE_BIN_PATH",),
}


class InstallationError(RuntimeError):
	"""Base error for an installation that cannot be completed."""


class InstallationConflict(InstallationError):
	"""Raised when installation would overwrite user-managed content."""

	def __init__(self, paths: Iterable[Path]):
		self.paths = tuple(sorted(paths, key=lambda path: path.as_posix()))
		super().__init__(
			"Refusing to overwrite modified or unknown files: "
			+ ", ".join(path.as_posix() for path in self.paths)
		)


@dataclass(frozen=True)
class InstallationResult:
	"""Summary of a completed or simulated installation."""

	actions: tuple[str, ...]
	warnings: tuple[str, ...]
	dry_run: bool


def _digest(content: str) -> str:
	return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _read_text(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _destination(project: Path, relative: str | Path) -> Path:
	relative_path = Path(relative)
	if relative_path.is_absolute() or ".." in relative_path.parts:
		raise InstallationError(f"Unsafe managed path: {relative_path.as_posix()}")
	destination = project / relative_path
	try:
		destination.resolve(strict=False).relative_to(project)
	except ValueError as error:
		raise InstallationError(
			f"Managed path resolves outside the project: {relative_path.as_posix()}"
		) from error
	return destination


def _load_manifest(project: Path) -> dict:
	path = _destination(project, MANIFEST_PATH)
	if not path.exists():
		return {"schema": MANIFEST_SCHEMA, "version": None, "agents": [], "files": {}}
	try:
		manifest = json.loads(_read_text(path))
	except (OSError, json.JSONDecodeError) as error:
		raise InstallationError(f"Cannot read {MANIFEST_PATH.as_posix()}: {error}") from error
	if (
		manifest.get("schema") != MANIFEST_SCHEMA
		or not isinstance(manifest.get("files"), dict)
		or not isinstance(manifest.get("agents", []), list)
	):
		raise InstallationError(f"Unsupported or invalid manifest at {MANIFEST_PATH.as_posix()}")
	for relative, record in manifest["files"].items():
		if not isinstance(relative, str) or not isinstance(record, dict):
			raise InstallationError(f"Invalid file record in {MANIFEST_PATH.as_posix()}")
		_destination(project, relative)
	return manifest


def _managed_block(content: str) -> str | None:
	pattern = re.compile(
		re.escape(AGENTS_START) + r".*?" + re.escape(AGENTS_END),
		re.DOTALL,
	)
	match = pattern.search(content)
	return match.group(0) if match else None


def _merge_block(existing: str, desired_block: str) -> str:
	current_block = _managed_block(existing)
	if current_block is not None:
		return existing.replace(current_block, desired_block, 1)
	if not existing.strip():
		return desired_block + "\n"
	return existing.rstrip() + "\n\n" + desired_block + "\n"


def _remove_block(existing: str) -> str:
	block = _managed_block(existing)
	if block is None:
		return existing
	before, _, after = existing.partition(block)
	return (before.rstrip() + "\n\n" + after.lstrip()).strip() + (
		"\n" if before.strip() or after.strip() else ""
	)


def _existing_newline(path: Path) -> str:
	if not path.exists():
		return "\n"
	with path.open("r", encoding="utf-8", newline="") as stream:
		return "\r\n" if "\r\n" in stream.read() else "\n"


def _atomic_write(path: Path, content: str) -> None:
	newline = _existing_newline(path)
	path.parent.mkdir(parents=True, exist_ok=True)
	handle, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
	temporary = Path(temporary_name)
	try:
		with os.fdopen(handle, "w", encoding="utf-8", newline=newline) as stream:
			stream.write(content)
		os.replace(temporary, path)
	finally:
		if temporary.exists():
			temporary.unlink()


def _manifest_content(agents: set[str], records: dict[str, dict[str, str]]) -> str:
	return (
		json.dumps(
			{
				"schema": MANIFEST_SCHEMA,
				"version": __version__,
				"agents": sorted(agents),
				"files": dict(sorted(records.items())),
			},
			indent=2,
		)
		+ "\n"
	)


def detect_agents(project: Path) -> tuple[str, ...]:
	"""Return the agents project appears to use, in SUPPORTED_AGENTS order."""
	project = project.resolve()
	if not project.is_dir():
		raise InstallationError(f"Project directory does not exist: {project}")

	# A previous installation is the most reliable signal: it makes a bare `init` refresh
	# exactly what is already installed instead of re-guessing.
	installed = _load_manifest(project).get("agents") or ()
	if installed:
		return tuple(agent for agent in SUPPORTED_AGENTS if agent in installed)

	found = {
		agent
		for agent, markers in AGENT_MARKERS.items()
		if any((project / marker).exists() for marker in markers)
	}
	found.update(
		agent
		for agent, variables in AGENT_ENVIRONMENT.items()
		if any(variable in os.environ for variable in variables)
	)
	# AGENTS.md is a cross-tool convention, so its presence alone identifies no agent.
	# It only points at OpenCode once this kit has written its section into it.
	agents_file = project / "AGENTS.md"
	if agents_file.is_file() and AGENTS_START in agents_file.read_text(
		encoding="utf-8", errors="replace"
	):
		found.add("opencode")
	return tuple(agent for agent in SUPPORTED_AGENTS if agent in found)


def install(
	project: Path,
	agents: Iterable[str],
	*,
	force: bool = False,
	dry_run: bool = False,
) -> InstallationResult:
	"""Install guidance for agents into project without clobbering user edits."""
	project = project.resolve()
	if not project.is_dir():
		raise InstallationError(f"Project directory does not exist: {project}")

	requested = set(agents)
	rendered = render_agents(sorted(requested))
	desired = {item.path.as_posix(): item for item in rendered}
	if len(desired) != len(rendered):
		raise InstallationError("Multiple rendered assets target the same project path")

	manifest = _load_manifest(project)
	previous_records: dict[str, dict[str, str]] = manifest["files"]
	next_records = {
		path: dict(record)
		for path, record in previous_records.items()
		if record.get("agent") not in requested
	}
	next_agents = set(manifest.get("agents", [])) | requested
	conflicts: list[Path] = []
	warnings: list[str] = []
	writes: dict[Path, str] = {}
	removals: list[Path] = []
	actions: list[str] = []

	for relative, item in desired.items():
		path = _destination(project, item.path)
		previous = previous_records.get(relative)
		if item.merge_block:
			existing = _read_text(path) if path.exists() else ""
			current_block = _managed_block(existing)
			if current_block is not None:
				is_known = previous is not None and _digest(current_block) == previous.get("sha256")
				if current_block != item.content and not is_known and not force:
					conflicts.append(item.path)
					continue
			merged = _merge_block(existing, item.content)
			if merged != existing:
				writes[path] = merged
				actions.append(f"update {relative}" if path.exists() else f"create {relative}")
			else:
				actions.append(f"unchanged {relative}")
			next_records[relative] = {
				"agent": item.agent,
				"sha256": _digest(item.content),
				"kind": "block",
			}
			continue

		existing = _read_text(path) if path.exists() else None
		known_unchanged = (
			existing is not None
			and previous is not None
			and _digest(existing) == previous.get("sha256")
		)
		if existing is not None and existing != item.content and not known_unchanged and not force:
			conflicts.append(item.path)
			continue
		if existing != item.content:
			writes[path] = item.content
			actions.append(f"update {relative}" if existing is not None else f"create {relative}")
		else:
			actions.append(f"unchanged {relative}")
		next_records[relative] = {
			"agent": item.agent,
			"sha256": _digest(item.content),
			"kind": "file",
		}

	for relative, record in previous_records.items():
		if record.get("agent") not in requested or relative in desired:
			continue
		path = _destination(project, relative)
		if not path.exists():
			actions.append(f"forget missing {relative}")
			continue
		existing = _read_text(path)
		if record.get("kind") == "block":
			block = _managed_block(existing)
			if block is not None and _digest(block) == record.get("sha256"):
				# The file itself may predate the kit, so strip the block but keep the file.
				writes[path] = _remove_block(existing)
				actions.append(f"remove obsolete block from {relative}")
			else:
				warnings.append(f"Kept modified obsolete block in {relative}")
			continue
		if _digest(existing) == record.get("sha256"):
			removals.append(path)
			actions.append(f"remove obsolete {relative}")
		else:
			warnings.append(f"Kept modified obsolete file {relative}")

	if conflicts:
		raise InstallationConflict(conflicts)

	manifest_text = _manifest_content(next_agents, next_records)
	manifest_file = _destination(project, MANIFEST_PATH)
	if not manifest_file.exists() or _read_text(manifest_file) != manifest_text:
		writes[manifest_file] = manifest_text
		actions.append(
			f"update {MANIFEST_PATH.as_posix()}"
			if manifest_file.exists()
			else f"create {MANIFEST_PATH.as_posix()}"
		)

	if not dry_run:
		for path in removals:
			path.unlink()
		for path, content in writes.items():
			_atomic_write(path, content)

	return InstallationResult(tuple(actions), tuple(warnings), dry_run)
