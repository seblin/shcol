import platform
import sys

ALLOW_EXCEEDING = True
ENCODING = 'utf-8'
HIDE_DOTTED = (not platform.system() == 'Windows')
LINE_WIDTH = None
LINE_WIDTH_FALLBACK = 80
LINESEP = '\n'
PRINT_STREAM = sys.stdout
SORT_ITEMS = False
SPACING = 2
TERMINAL_FD = sys.__stdout__.fileno()
