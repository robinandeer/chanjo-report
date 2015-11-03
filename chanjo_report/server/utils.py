# -*- coding: utf-8 -*-
"""Utils has nothing to do with models and views."""
from datetime import datetime


def get_current_time():
    """Simply get the current UTC timestamp."""
    return datetime.utcnow()


def pretty_date(date, default=None):
    """Return string representing "time since": 3 days ago, 5 hours ago.

    Ref: https://bitbucket.org/danjac/newsmeme/src/a281babb9ca3/newsmeme/
    """
    if default is None:
        default = 'just now'

    now = datetime.utcnow()
    diff = now - date

    periods = ((diff.days / 365, 'year', 'years'),
               (diff.days / 30, 'month', 'months'),
               (diff.days / 7, 'week', 'weeks'),
               (diff.days, 'day', 'days'),
               (diff.seconds / 3600, 'hour', 'hours'),
               (diff.seconds / 60, 'minute', 'minutes'),
               (diff.seconds, 'second', 'seconds'))

    for period, singular, plural in periods:
        if not period:
            continue
        if period == 1:
            return "%d %s ago" % (period, singular)
        else:
            return "%d %s ago" % (period, plural)
    return default
