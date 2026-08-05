from pathlib import Path

from imfusion_sdk_agent_kit.cli import main


def test_cli_installs_comma_separated_agents(tmp_path: Path, capsys) -> None:
	exit_code = main(
		["init", "--agent", "cursor,claude", "--project", str(tmp_path)]
	)

	assert exit_code == 0
	assert (tmp_path / ".cursor/rules").is_dir()
	assert (tmp_path / ".claude/rules").is_dir()
	assert "create .imfusion-sdk-agent-kit/manifest.json" in capsys.readouterr().out


def test_cli_reports_conflict(tmp_path: Path, capsys) -> None:
	collision = tmp_path / ".cursor/rules/cpp-guidelines.mdc"
	collision.parent.mkdir(parents=True)
	collision.write_text("custom\n", encoding="utf-8")

	exit_code = main(["init", "--agent", "cursor", "--project", str(tmp_path)])

	assert exit_code == 2
	assert "Re-run with --force" in capsys.readouterr().err


def test_cli_dry_run_prefixes_actions(tmp_path: Path, capsys) -> None:
	exit_code = main(
		["init", "--agent", "opencode", "--project", str(tmp_path), "--dry-run"]
	)

	assert exit_code == 0
	assert "Would create AGENTS.md" in capsys.readouterr().out
	assert list(tmp_path.iterdir()) == []
