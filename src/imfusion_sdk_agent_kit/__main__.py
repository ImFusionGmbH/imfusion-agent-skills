"""Allow ``python -m imfusion_sdk_agent_kit`` execution."""

from .cli import main

if __name__ == "__main__":
	raise SystemExit(main())
