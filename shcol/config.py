# -*- coding: utf-8 -*
# Copyright (c) 2013-2014, Sebastian Linke

# Released under the Simplified BSD license 
# (see LICENSE file for details).

import platform
import sys

ENCODING = 'utf-8'
HIDE_DOTTED = (not platform.system() == 'Windows')
LINE_WIDTH = None
LINE_WIDTH_FALLBACK = 80
LINESEP = '\n'
PRINT_STREAM = sys.stdout
SORT_ITEMS = False
SPACING = 2
TERMINAL_FD = sys.__stdout__.fileno()
