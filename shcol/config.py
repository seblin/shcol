# -*- coding: utf-8 -*-
# Copyright (c) 2013-2015, Sebastian Linke

# Released under the Simplified BSD license
# (see LICENSE file for details).

"""
Constants that are used by `shcol` in many places. This is meant to modified (if
needed) only *before* running `shcol`, since most of these constants are only
read during initialization of the `shcol`-package.
"""
import logging
import os
import sys

ERROR_STREAM = sys.stderr
INPUT_STREAM = sys.stdin
LINE_WIDTH = None
LINESEP = '\n'
LOGGER = logging.getLogger('shol')
MAKE_UNIQUE = False
ON_WINDOWS = 'windows' in os.getenv('os', '').lower()
PY_VERSION = sys.version_info[:2]
SORT_ITEMS = False
SPACING = 2
STARTER = os.path.join('bin', 'shcol' + ('.bat' if ON_WINDOWS else ''))
TERMINAL_STREAM = sys.stdout
UNICODE_TYPE = type(u'')

ENCODING = getattr(TERMINAL_STREAM, 'encoding', 'utf-8')
