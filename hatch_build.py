"""Hatch build hook that compiles Babel translation catalogues into .mo files.

The .mo files are gitignored, so they are generated here at build time and
force-included in the wheel through ``artifacts`` in ``pyproject.toml``.
"""

from pathlib import Path

from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po
from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class TranslationBuildHook(BuildHookInterface):
    PLUGIN_NAME = "custom"

    def initialize(self, version, build_data):
        if self.target_name != "wheel":
            return
        package_dir = Path(self.root) / "chanjo_report"
        for po_path in package_dir.rglob("messages.po"):
            with po_path.open("rb") as po_file:
                catalog = read_po(po_file)
            mo_path = po_path.with_suffix(".mo")
            with mo_path.open("wb") as mo_file:
                write_mo(mo_file, catalog)
