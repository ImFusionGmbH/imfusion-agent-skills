from pathlib import Path

from imfusion_sdk_agent_kit.renderers import AGENTS_END, AGENTS_START, parse_mdc, render_agents


def test_parse_mdc_accepts_crlf() -> None:
	frontmatter, body = parse_mdc(
		"---\r\ndescription: Example\r\nglobs: **/*.cpp\r\nalwaysApply: false\r\n---\r\nBody\r\n"
	)

	assert frontmatter == {
		"description": "Example",
		"globs": "**/*.cpp",
		"alwaysApply": "false",
	}
	assert body == "Body"


def test_render_all_agents_to_native_locations() -> None:
	rendered = render_agents(("cursor", "claude", "opencode"))
	by_path = {item.path.as_posix(): item for item in rendered}

	assert ".cursor/rules/cpp-guidelines.mdc" in by_path
	assert ".cursor/skills/create-imfusion-plugin/SKILL.md" in by_path
	assert ".claude/rules/cpp-guidelines.md" in by_path
	assert ".claude/skills/create-imfusion-plugin/SKILL.md" in by_path
	assert ".opencode/skills/create-imfusion-plugin/SKILL.md" in by_path
	assert ".opencode/references/ml-operation-header-template.h" in by_path
	assert by_path["AGENTS.md"].merge_block
	assert AGENTS_START in by_path["AGENTS.md"].content
	assert AGENTS_END in by_path["AGENTS.md"].content


def test_claude_rules_translate_scoping_and_template_links() -> None:
	rendered = {item.path: item.content for item in render_agents(("claude",))}

	cpp_rule = rendered[Path(".claude/rules/cpp-guidelines.md")]
	assert "paths:" in cpp_rule
	assert '"**/*.cpp"' in cpp_rule

	always_rule = rendered[Path(".claude/rules/core-principles.md")]
	assert "paths:" not in always_rule

	ml_rule = rendered[Path(".claude/rules/ml-operations.md")]
	assert "@ml-operation-header-template.h" not in ml_rule
	assert ".claude/rules/ml-operation-header-template.h" in ml_rule


def test_skills_are_tool_neutral() -> None:
	rendered = {item.path: item.content for item in render_agents(("cursor", "claude"))}

	cursor_skill = rendered[Path(".cursor/skills/create-imfusion-plugin/SKILL.md")]
	claude_skill = rendered[Path(".claude/skills/create-imfusion-plugin/SKILL.md")]
	assert cursor_skill == claude_skill
	assert ".cursor/" not in cursor_skill
