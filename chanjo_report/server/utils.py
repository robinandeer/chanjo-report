# -*- coding: utf-8 -*-
import pdfkit

from datetime import datetime
from io import BytesIO

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


def html_to_pdf_file(
    html_string, orientation, dpi=96, margins=["1.5cm", "1cm", "1cm", "1cm"], zoom=1
) -> BytesIO:
    """Creates a pdf file from the content of an HTML file
    Args:
        html_string(string): an HTML string to be rendered as PDF
        orientation(string): landscape, portrait
        dpi(int): dot density of the page to be printed
        margins(list): [ margin-top, margin-right, margin-bottom, margin-left], in cm
        zoom(float): change the size of the content on the pages

    Returns:
        bytes_file(BytesIO): a BytesIO file
    """
    options = {
        "page-size": "A4",
        "zoom": zoom,
        "orientation": orientation,
        "encoding": "UTF-8",
        "dpi": dpi,
        "margin-top": margins[0],
        "margin-right": margins[1],
        "margin-bottom": margins[2],
        "margin-left": margins[3],
        "enable-local-file-access": None,
    }
    pdf = pdfkit.from_string(html_string, False, options=options, verbose=True)
    bytes_file = BytesIO(pdf)
    return bytes_file
