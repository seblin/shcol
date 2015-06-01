# -*- coding: utf-8 -*-
# Copyright (c) 2013-2015, Sebastian Linke

# Released under the Simplified BSD license
# (see LICENSE file for details).

"""
Constants that are used by `shcol` in many places. This is meant to modified (if
needed) only *before* running `shcol`, since most of these constants are only
read during initialization of the `shcol`-package.
"""

import os
import sys

ENCODING = sys.stdout.encoding or 'utf-8'
ERROR_STREAM = sys.stderr
INPUT_STREAM = sys.stdin
LINE_WIDTH = None
LINESEP = '\n'
MAKE_UNIQUE = False
NEEDS_DECODING = (sys.version_info < (3, 0))
ON_WINDOWS = sys.platform.startswith('win')
PY_VERSION = sys.version_info
SORT_ITEMS = False
SPACING = 2
STARTER = os.path.join('bin', 'shcol' + ('.bat' if ON_WINDOWS else ''))
TERMINAL_STREAM = sys.stdout
