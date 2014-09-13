# -*- coding: utf-8 -*-
"""Extract interesting data from a Chanjo SQL database.

Built-in abilities:

  - average metrics: coverage, completeness (interval)
  - samples (raw :class:`chanjo.store.Sample` instances)
  - subset (elements passing a filter criteria)
"""
from __future__ import absolute_import, unicode_literals

from .core import key_metrics
