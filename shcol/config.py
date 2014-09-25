# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014, Sebastian Linke

# Released under the Simplified BSD license
# (see LICENSE file for details).

"""
Constants that are used by `shcol` in many places. This is meant to modified (if
needed) only *before* running `shcol`, since most of these constants are only
read during initialization of the `shcol`-package.
"""

import sys

ENCODING = 'utf-8'
ERROR_STREAM = sys.stderr
INPUT_STREAM = sys.stdin
LINE_WIDTH = None
LINE_WIDTH_FALLBACK = 80
LINESEP = '\n'
OUTPUT_STREAM = sys.stdout
SORT_ITEMS = False
SPACING = 2
TERMINAL_FD = sys.__stdout__.fileno()
