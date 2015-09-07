# -*- coding: utf-8 -*-
"""Utilities related to entry point interfaces loaded by the CLI."""
from pkg_resources import iter_entry_points


def iter_interfaces(ep_key='chanjo_report.interfaces'):
    """Yield all the installed Chanjo Report interfaces.

    Args:
        ep_key (string): Entry point key to iterate over

    Yields:
        object: Entry point object
    """
    for entry_point in iter_entry_points(ep_key):
        yield entry_point


def list_interfaces():
    """List all installed interfaces by name."""
    return [interface.name for interface in iter_interfaces()]
