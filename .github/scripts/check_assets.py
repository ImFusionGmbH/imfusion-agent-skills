"""Fail the build if a distribution is missing bundled rules, skills, or references."""

from __future__ import annotations

import sys
import tarfile
import zipfile
from pathlib import Path


def _summarize(names: list[str]) -> dict[str, int]:
	return {
		"rules": len(
			[name for name in names if "/assets/rules/" in name and name.endswith(".mdc")]
		),
		"skills": len([name for name in names if name.endswith("/SKILL.md")]),
		"references": len([name for name in names if "/assets/references/" in name]),
	}


def main() -> int:
	distributions = sorted(Path("dist").glob("*.whl")) + sorted(Path("dist").glob("*.tar.gz"))
	if not distributions:
		print("No distributions found in dist/", file=sys.stderr)
		return 1

	failed = False
	for distribution in distributions:
		if distribution.suffix == ".whl":
			with zipfile.ZipFile(distribution) as archive:
				counts = _summarize(archive.namelist())
		else:
			with tarfile.open(distribution) as archive:
				counts = _summarize(archive.getnames())
		missing = [kind for kind, count in counts.items() if count == 0]
		print(f"{distribution.name}: {counts}")
		if missing:
			print(f"{distribution.name} is missing {', '.join(missing)}", file=sys.stderr)
			failed = True
	return 1 if failed else 0


if __name__ == "__main__":
	raise SystemExit(main())
