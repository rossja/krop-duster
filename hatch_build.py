"""
Hatch build hook to download VBW (Very Bad Words) dataset during installation.

This hook runs during `uv sync` or package installation to ensure the VBW
dataset is available for taboo word detection.
"""

import logging
import urllib.request
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


logger = logging.getLogger(__name__)

VBW_URL = "https://raw.githubusercontent.com/hypernewbie/vbw/main/vbw.csv"


class CustomBuildHook(BuildHookInterface):
    """Custom build hook to download VBW dataset."""

    PLUGIN_NAME = "custom"

    def initialize(self, version: str, build_data: dict) -> None:
        """
        Initialize hook - downloads VBW dataset if not present.

        Args:
            version: The version being built
            build_data: Build configuration data
        """
        # Download VBW dataset to package data directory
        data_dir = Path(self.root) / "krop_duster" / "data"
        data_dir.mkdir(parents=True, exist_ok=True)

        vbw_path = data_dir / "vbw.csv"

        # Create __init__.py if it doesn't exist
        init_path = data_dir / "__init__.py"
        if not init_path.exists():
            init_path.touch()

        if not vbw_path.exists():
            print(f"Downloading VBW dataset to {vbw_path}...")
            try:
                urllib.request.urlretrieve(VBW_URL, vbw_path)
                print(f"Successfully downloaded VBW dataset ({vbw_path.stat().st_size} bytes)")
            except Exception as e:
                print(f"Warning: Failed to download VBW dataset: {e}")
                print("VBW dataset will be downloaded on first use.")
        else:
            print(f"VBW dataset already exists at {vbw_path}")
