# -*- coding: utf-8 -*-
"""
chanjo_report
~~~~~~~~~~~~~

Chanjo Report automatically renders a coverage report from Chanjo ouput.

:copyright: (c) 2014 by Robin Andeer
:licence: MIT, see LICENCE for more details
"""
from pkg_resources import get_distribution

# generate your own AsciiArt at:
# patorjk.com/software/taag/#f=Calvin%20S&t=Chanjo Report
__banner__ = r"""
╔═╗┬ ┬┌─┐┌┐┌ ┬┌─┐  ╦═╗┌─┐┌─┐┌─┐┬─┐┌┬┐
║  ├─┤├─┤│││ ││ │  ╠╦╝├┤ ├─┘│ │├┬┘ │   by Robin Andeer
╚═╝┴ ┴┴ ┴┘└┘└┘└─┘  ╩╚═└─┘┴  └─┘┴└─ ┴
"""

__title__ = 'chanjo-report'
__summary__ = 'Automatically renders coverage reports from Chanjo ouput.'
__uri__ = 'https://github.com/robinandeer/chanjo-report'

__version__ = get_distribution(__title__).version

__author__ = 'Robin Andeer'
__email__ = 'robin.andeer@gmail.com'

__license__ = 'MIT'
__copyright__ = 'Copyright 2014 Robin Andeer'
