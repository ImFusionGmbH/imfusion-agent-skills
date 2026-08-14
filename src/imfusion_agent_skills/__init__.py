"""Install ImFusion SDK guidance for supported coding agents."""

from importlib.metadata import PackageNotFoundError, version

try:
	__version__ = version("imfusion-agent-skills")
except PackageNotFoundError:
	__version__ = "0+unknown"
