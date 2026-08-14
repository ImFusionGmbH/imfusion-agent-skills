from pathlib import Path

import pytest

from imfusion_agent_skills import __version__
from imfusion_agent_skills.cli import main
from imfusion_agent_skills.installer import AGENT_ENVIRONMENT


@pytest.fixture
def clean_environment(monkeypatch: pytest.MonkeyPatch) -> None:
	"""Hide the agent that runs the test suite so detection sees only the project."""
	for variables in AGENT_ENVIRONMENT.values():
		for variable in variables:
			monkeypatch.delenv(variable, raising=False)


def test_cli_installs_comma_separated_agents(tmp_path: Path, capsys) -> None:
	exit_code = main(["init", str(tmp_path), "--agent", "cursor,claude"])

	assert exit_code == 0
	assert (tmp_path / ".cursor/rules").is_dir()
	assert (tmp_path / ".claude/rules").is_dir()
	assert "create .imfusion-agent-skills/manifest.json" in capsys.readouterr().out


def test_cli_reports_conflict(tmp_path: Path, capsys) -> None:
	collision = tmp_path / ".cursor/rules/cpp-guidelines.mdc"
	collision.parent.mkdir(parents=True)
	collision.write_text("custom\n", encoding="utf-8")

	exit_code = main(["init", str(tmp_path), "--agent", "cursor"])

	assert exit_code == 2
	assert "Re-run with --force" in capsys.readouterr().err


def test_cli_dry_run_prefixes_actions(tmp_path: Path, capsys) -> None:
	exit_code = main(["init", str(tmp_path), "--agent", "opencode", "--dry-run"])

	assert exit_code == 0
	assert "[dry-run] create AGENTS.md" in capsys.readouterr().out
	assert list(tmp_path.iterdir()) == []


def test_cli_rejects_unknown_agent(tmp_path: Path, capsys) -> None:
	with pytest.raises(SystemExit) as caught:
		main(["init", str(tmp_path), "--agent", "windsurf"])

	assert caught.value.code == 2
	error = capsys.readouterr().err
	assert "unsupported agent(s): windsurf" in error
	assert list(tmp_path.iterdir()) == []


def test_cli_accepts_legacy_project_option(tmp_path: Path) -> None:
	exit_code = main(["init", "--agent", "cursor", "--project", str(tmp_path)])

	assert exit_code == 0
	assert (tmp_path / ".cursor/rules").is_dir()


@pytest.mark.usefixtures("clean_environment")
def test_cli_detects_the_agent_when_the_flag_is_omitted(tmp_path: Path, capsys) -> None:
	(tmp_path / ".cursor").mkdir()

	exit_code = main(["init", str(tmp_path)])

	assert exit_code == 0
	assert "Detected agent(s): cursor" in capsys.readouterr().out
	assert (tmp_path / ".cursor/skills").is_dir()
	assert not (tmp_path / ".claude").exists()


@pytest.mark.usefixtures("clean_environment")
def test_cli_reuses_the_agents_from_a_previous_install(tmp_path: Path, capsys) -> None:
	main(["init", str(tmp_path), "--agent", "cursor,claude"])
	capsys.readouterr()

	exit_code = main(["init", str(tmp_path)])

	assert exit_code == 0
	assert "Detected agent(s): cursor, claude" in capsys.readouterr().out


@pytest.mark.usefixtures("clean_environment")
def test_cli_explains_how_to_choose_when_detection_fails(tmp_path: Path, capsys) -> None:
	exit_code = main(["init", str(tmp_path)])

	assert exit_code == 2
	error = capsys.readouterr().err
	assert "no agent detected" in error
	assert "cursor, claude, opencode" in error
	assert list(tmp_path.iterdir()) == []


def test_cli_reports_version(capsys) -> None:
	with pytest.raises(SystemExit) as caught:
		main(["--version"])

	assert caught.value.code == 0
	assert __version__ in capsys.readouterr().out
