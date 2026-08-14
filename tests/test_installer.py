import json
from pathlib import Path

import pytest

import imfusion_agent_skills.installer as installer_module
from imfusion_agent_skills.installer import (
	AGENT_ENVIRONMENT,
	MANIFEST_PATH,
	InstallationConflict,
	InstallationError,
	detect_agents,
	install,
)
from imfusion_agent_skills.renderers import AGENTS_END, AGENTS_START, RenderedFile


@pytest.fixture
def clean_environment(monkeypatch: pytest.MonkeyPatch) -> None:
	"""Hide the agent that runs the test suite so detection sees only the project."""
	for variables in AGENT_ENVIRONMENT.values():
		for variable in variables:
			monkeypatch.delenv(variable, raising=False)


def test_first_install_and_idempotent_rerun(tmp_path: Path) -> None:
	first = install(tmp_path, ("cursor", "claude"))

	assert (tmp_path / ".cursor/rules/cpp-guidelines.mdc").is_file()
	assert (tmp_path / ".claude/skills/create-imfusion-plugin/SKILL.md").is_file()
	manifest = json.loads((tmp_path / MANIFEST_PATH).read_text(encoding="utf-8"))
	assert manifest["agents"] == ["claude", "cursor"]
	assert first.actions

	second = install(tmp_path, ("cursor", "claude"))
	assert second.actions
	assert all(action.startswith("unchanged ") for action in second.actions)


def test_unknown_collision_aborts_without_partial_writes(tmp_path: Path) -> None:
	collision = tmp_path / ".cursor/rules/cpp-guidelines.mdc"
	collision.parent.mkdir(parents=True)
	collision.write_text("user content\n", encoding="utf-8")

	with pytest.raises(InstallationConflict) as caught:
		install(tmp_path, ("cursor",))

	assert Path(".cursor/rules/cpp-guidelines.mdc") in caught.value.paths
	assert collision.read_text(encoding="utf-8") == "user content\n"
	assert not (tmp_path / ".cursor/skills").exists()
	assert not (tmp_path / MANIFEST_PATH).exists()


def test_force_replaces_collision(tmp_path: Path) -> None:
	collision = tmp_path / ".cursor/rules/cpp-guidelines.mdc"
	collision.parent.mkdir(parents=True)
	collision.write_text("user content\n", encoding="utf-8")

	install(tmp_path, ("cursor",), force=True)

	assert "# C++ Guidelines" in collision.read_text(encoding="utf-8")


def test_modified_managed_file_is_a_conflict(tmp_path: Path) -> None:
	install(tmp_path, ("cursor",))
	managed = tmp_path / ".cursor/rules/cpp-guidelines.mdc"
	managed.write_text("locally modified\n", encoding="utf-8")

	with pytest.raises(InstallationConflict):
		install(tmp_path, ("cursor",))


def test_dry_run_does_not_write(tmp_path: Path) -> None:
	result = install(tmp_path, ("cursor",), dry_run=True)

	assert result.dry_run
	assert result.actions
	assert list(tmp_path.iterdir()) == []


def test_manifest_rejects_path_traversal(tmp_path: Path) -> None:
	manifest = tmp_path / MANIFEST_PATH
	manifest.parent.mkdir()
	manifest.write_text(
		json.dumps(
			{
				"schema": 1,
				"agents": ["cursor"],
				"files": {
					"../outside.txt": {
						"agent": "cursor",
						"sha256": "invalid",
						"kind": "file",
					}
				},
			}
		),
		encoding="utf-8",
	)

	with pytest.raises(InstallationError, match="Unsafe managed path"):
		install(tmp_path, ("cursor",))


def test_opencode_preserves_existing_agents_content(tmp_path: Path) -> None:
	agents_file = tmp_path / "AGENTS.md"
	agents_file.write_text("# Existing project guidance\n", encoding="utf-8")

	install(tmp_path, ("opencode",))

	content = agents_file.read_text(encoding="utf-8")
	assert content.startswith("# Existing project guidance")
	assert AGENTS_START in content
	assert (tmp_path / ".opencode/skills/create-imfusion-app/SKILL.md").is_file()


def test_opencode_preserves_existing_line_endings(tmp_path: Path) -> None:
	agents_file = tmp_path / "AGENTS.md"
	agents_file.write_bytes(b"# Existing project guidance\r\n")

	install(tmp_path, ("opencode",))

	written = agents_file.read_bytes()
	assert b"\r\n" in written
	assert written.count(b"\n") == written.count(b"\r\n")


def test_obsolete_block_is_removed_without_deleting_the_file(
	tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
	agents_file = tmp_path / "AGENTS.md"
	agents_file.write_text("# Existing project guidance\n", encoding="utf-8")
	install(tmp_path, ("opencode",))

	monkeypatch.setattr(installer_module, "render_agents", lambda agents: [])
	result = install(tmp_path, ("opencode",))

	assert "remove obsolete block from AGENTS.md" in result.actions
	content = agents_file.read_text(encoding="utf-8")
	assert content == "# Existing project guidance\n"
	assert AGENTS_START not in content


def test_modified_opencode_block_is_a_conflict(tmp_path: Path) -> None:
	install(tmp_path, ("opencode",))
	agents_file = tmp_path / "AGENTS.md"
	content = agents_file.read_text(encoding="utf-8")
	agents_file.write_text(content.replace("# Algorithm Pattern", "# Local edit"), encoding="utf-8")

	with pytest.raises(InstallationConflict):
		install(tmp_path, ("opencode",))


def test_obsolete_unchanged_file_is_removed(
	tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
	old = RenderedFile(Path(".cursor/rules/old.mdc"), "old\n", "cursor")
	monkeypatch.setattr(installer_module, "render_agents", lambda agents: [old])
	install(tmp_path, ("cursor",))
	assert (tmp_path / old.path).exists()

	monkeypatch.setattr(installer_module, "render_agents", lambda agents: [])
	result = install(tmp_path, ("cursor",))

	assert not (tmp_path / old.path).exists()
	assert "remove obsolete .cursor/rules/old.mdc" in result.actions


def test_modified_obsolete_file_is_kept_and_forgotten(
	tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
	old = RenderedFile(Path(".cursor/rules/old.mdc"), "old\n", "cursor")
	monkeypatch.setattr(installer_module, "render_agents", lambda agents: [old])
	install(tmp_path, ("cursor",))
	path = tmp_path / old.path
	path.write_text("custom\n", encoding="utf-8")

	monkeypatch.setattr(installer_module, "render_agents", lambda agents: [])
	result = install(tmp_path, ("cursor",))

	assert path.read_text(encoding="utf-8") == "custom\n"
	assert result.warnings == ("Kept modified obsolete file .cursor/rules/old.mdc",)
	manifest = json.loads((tmp_path / MANIFEST_PATH).read_text(encoding="utf-8"))
	assert old.path.as_posix() not in manifest["files"]


@pytest.mark.usefixtures("clean_environment")
def test_detect_agents_finds_nothing_in_an_empty_project(tmp_path: Path) -> None:
	assert detect_agents(tmp_path) == ()


@pytest.mark.usefixtures("clean_environment")
def test_detect_agents_reads_project_markers(tmp_path: Path) -> None:
	(tmp_path / ".opencode").mkdir()
	(tmp_path / "CLAUDE.md").write_text("# guidance\n", encoding="utf-8")

	assert detect_agents(tmp_path) == ("claude", "opencode")


@pytest.mark.usefixtures("clean_environment")
def test_detect_agents_reads_agent_environment(
	tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
	monkeypatch.setenv("CURSOR_AGENT", "1")

	assert detect_agents(tmp_path) == ("cursor",)


@pytest.mark.usefixtures("clean_environment")
def test_detect_agents_ignores_unmanaged_agents_file(tmp_path: Path) -> None:
	(tmp_path / "AGENTS.md").write_text("# project guidance\n", encoding="utf-8")

	assert detect_agents(tmp_path) == ()


@pytest.mark.usefixtures("clean_environment")
def test_detect_agents_recognises_a_managed_agents_file(tmp_path: Path) -> None:
	(tmp_path / "AGENTS.md").write_text(
		f"# project guidance\n\n{AGENTS_START}\nrules\n{AGENTS_END}\n", encoding="utf-8"
	)

	assert detect_agents(tmp_path) == ("opencode",)


@pytest.mark.usefixtures("clean_environment")
def test_detect_agents_prefers_the_manifest_over_other_signals(tmp_path: Path) -> None:
	install(tmp_path, ("cursor",))
	(tmp_path / ".opencode").mkdir()

	assert detect_agents(tmp_path) == ("cursor",)
