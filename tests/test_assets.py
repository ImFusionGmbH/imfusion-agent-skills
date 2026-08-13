"""Validate the authored assets, independently of how they are rendered."""

import re
from importlib.resources import files

import pytest

from imfusion_sdk_agent_kit.renderers import parse_mdc

FRONTMATTER_LINE = re.compile(r"^[A-Za-z][A-Za-z0-9]*: \S")
SKILL_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
AGENT_DIRECTORIES = (".cursor/", ".claude/", ".opencode/")


def _assets():
	return files("imfusion_sdk_agent_kit").joinpath("assets")


def _rules() -> list[tuple[str, str]]:
	rules = _assets().joinpath("rules")
	return [
		(entry.name, entry.read_text(encoding="utf-8"))
		for entry in sorted(rules.iterdir(), key=lambda item: item.name)
		if entry.name.endswith(".mdc")
	]


def _skills() -> list[tuple[str, str]]:
	skills = _assets().joinpath("skills")
	return [
		(entry.name, entry.joinpath("SKILL.md").read_text(encoding="utf-8"))
		for entry in sorted(skills.iterdir(), key=lambda item: item.name)
		if entry.is_dir()
	]


def _reference_names() -> set[str]:
	return {entry.name for entry in _assets().joinpath("references").iterdir()}


@pytest.mark.parametrize("name, text", _rules())
def test_rule_frontmatter_is_well_formed(name: str, text: str) -> None:
	assert text.startswith("---\n"), f"{name} must open with a frontmatter block"
	block = text.split("---\n", 2)[1]
	for line in block.splitlines():
		assert FRONTMATTER_LINE.match(line), f"{name} has a malformed frontmatter line: {line!r}"

	frontmatter, body = parse_mdc(text)
	assert frontmatter.get("description"), f"{name} needs a description for agent discovery"
	assert frontmatter.get("alwaysApply") in {"true", "false"}, f"{name} needs alwaysApply"
	assert body, f"{name} has no body"


@pytest.mark.parametrize("name, text", _rules())
def test_rule_references_exist(name: str, text: str) -> None:
	_, body = parse_mdc(text)
	referenced = {line[1:] for line in body.splitlines() if line.startswith("@")}
	missing = referenced - _reference_names()
	assert not missing, f"{name} references missing files: {sorted(missing)}"


@pytest.mark.parametrize("name, text", _skills())
def test_skill_name_matches_directory(name: str, text: str) -> None:
	# OpenCode rejects skills whose frontmatter name does not match the directory name.
	assert SKILL_NAME.match(name), f"{name} must be lowercase with single hyphens"
	assert text.startswith("---\n"), f"{name} must open with a frontmatter block"
	block = text.split("---\n", 2)[1]
	frontmatter, body = parse_mdc(text)
	assert frontmatter.get("name") == name, f"{name} declares a different name"
	assert "\ndescription:" in f"\n{block}", f"{name} needs a description"
	assert body, f"{name} has no body"


@pytest.mark.parametrize("name, text", _rules() + _skills())
def test_sources_stay_agent_neutral(name: str, text: str) -> None:
	found = [directory for directory in AGENT_DIRECTORIES if directory in text]
	assert not found, f"{name} hardcodes agent directories: {found}"
