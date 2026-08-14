"""Allow ``python -m imfusion_agent_skills`` execution."""

from .cli import main

if __name__ == "__main__":
	raise SystemExit(main())
