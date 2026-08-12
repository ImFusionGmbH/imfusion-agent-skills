"""Command-line interface for imfusion-sdk-agent-kit."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .installer import InstallationConflict, InstallationError, install
from .renderers import SUPPORTED_AGENTS


def _agents(value: str) -> tuple[str, ...]:
	agents = tuple(dict.fromkeys(part.strip().lower() for part in value.split(",") if part.strip()))
	if not agents:
		raise argparse.ArgumentTypeError("specify at least one agent")
	unknown = sorted(set(agents) - set(SUPPORTED_AGENTS))
	if unknown:
		raise argparse.ArgumentTypeError(
			f"unsupported agent(s): {', '.join(unknown)}; choose from {', '.join(SUPPORTED_AGENTS)}"
		)
	return agents


def build_parser() -> argparse.ArgumentParser:
	"""Create the CLI argument parser."""
	parser = argparse.ArgumentParser(
		prog="imfusion-sdk-agent-kit",
		description="Install ImFusion SDK rules and skills into a project.",
	)
	parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
	subparsers = parser.add_subparsers(dest="command", required=True)

	init = subparsers.add_parser("init", help="install rules and skills")
	init.add_argument(
		"--agent",
		required=True,
		type=_agents,
		help=f"comma-separated agents: {', '.join(SUPPORTED_AGENTS)}",
	)
	init.add_argument(
		"--project",
		type=Path,
		default=Path.cwd(),
		help="project directory (default: current directory)",
	)
	init.add_argument(
		"--dry-run",
		action="store_true",
		help="show changes without writing files",
	)
	init.add_argument(
		"--force",
		action="store_true",
		help="replace conflicting destination files",
	)
	return parser


def main(argv: Sequence[str] | None = None) -> int:
	"""Run the command-line interface."""
	args = build_parser().parse_args(argv)
	try:
		result = install(
			args.project,
			args.agent,
			force=args.force,
			dry_run=args.dry_run,
		)
	except InstallationConflict as error:
		print(f"Error: {error}", file=sys.stderr)
		print("Re-run with --force to replace these files.", file=sys.stderr)
		return 2
	except InstallationError as error:
		print(f"Error: {error}", file=sys.stderr)
		return 1

	prefix = "[dry-run] " if result.dry_run else ""
	for action in result.actions:
		print(prefix + action)
	for warning in result.warnings:
		print(f"Warning: {warning}", file=sys.stderr)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
