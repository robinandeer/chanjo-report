# -*- coding: utf-8 -*-
"""Utilities related to entry point interfaces loaded by the CLI."""
from importlib.metadata import entry_points


def iter_interfaces(ep_key='chanjo_report.interfaces'):
    """Yield all the installed Chanjo Report interfaces.

    Args:
        ep_key (string): Entry point key to iterate over

    Yields:
        object: Entry point object
    """
    eps = entry_points()
    # Adjust based on Python's version of importlib.metadata
    if hasattr(eps, 'select'):
        # Python >= 3.10
        for entry_point in eps.select(group=ep_key):
            yield entry_point
    else:
        # For Python < 3.10
        for entry_point in eps.get(ep_key, []):
            yield entry_point


def list_interfaces():
    """List all installed interfaces by name."""
    return [interface.name for interface in iter_interfaces()]
