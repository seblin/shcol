# -*- coding: utf-8 -*-
# Copyright (c) 2013-2016, Sebastian Linke

# Released under the Simplified BSD license
# (see LICENSE file for details).

"""
Detect terminal width on different platforms.
"""

import collections
import ctypes
import ctypes.util
import os

from .. import config

try:
    import ctypes.wintypes
    HAVE_WINTYPES = True
except (ImportError, ValueError):
    HAVE_WINTYPES = False

__all__ = ['get_terminal_width_info']

TerminalWidthInfo = collections.namedtuple(
    'TerminalWidthInfo', 'window_width, is_line_width'
)

def make_width_info(window_width, is_line_width=True):
    """
    Return a new `TerminalWidthInfo`-object.

    `window_width` must be an integer defining the width of the terminal window.

    `is_line_width` defines whether the window width matches the terminal's line
    width. At least on Windows it might happen that the terminal window is
    smaller than the terminal's line width.
    """
    return TerminalWidthInfo(window_width, is_line_width)


if config.ON_WINDOWS and HAVE_WINTYPES:
    class ConsoleScreenBufferInfo(ctypes.Structure):
        _fields_ = [
            ('dwSize', ctypes.wintypes._COORD),
            ('dwCursorPosition', ctypes.wintypes._COORD),
            ('wAttributes', ctypes.wintypes.WORD),
            ('srWindow', ctypes.wintypes.SMALL_RECT),
            ('dwMaximumWindowSize', ctypes.wintypes._COORD)
        ]

    GetStdHandle = ctypes.windll.kernel32.GetStdHandle
    GetStdHandle.restype = ctypes.wintypes.HANDLE
    GetStdHandle.argtypes = [ctypes.wintypes.DWORD]

    GetConsoleScreenBufferInfo = (
        ctypes.windll.kernel32.GetConsoleScreenBufferInfo
    )
    GetConsoleScreenBufferInfo.restype = ctypes.wintypes.BOOL
    GetConsoleScreenBufferInfo.argtypes = [
        ctypes.wintypes.HANDLE,
        ctypes.c_void_p,
    ]

    def get_std_handle(fd):
        if not 0 <= fd <= 2:
            raise ValueError('bad file descriptor')
        num_handle = (-10, -11, -12)[fd]
        return GetStdHandle(num_handle)

    def get_console_screen_buffer_info(handle):
        csbi = ConsoleScreenBufferInfo()
        GetConsoleScreenBufferInfo(handle, ctypes.byref(csbi))
        return csbi

    def terminal_width_impl(fd):
        config.LOGGER.debug('running `terminal_width_impl()` on Windows')
        handle = get_std_handle(fd)
        csbi = get_console_screen_buffer_info(handle)
        window = csbi.srWindow
        window_width = window.Right - window.Left + 1
        line_width = csbi.dwMaximumWindowSize.X
        return make_width_info(window_width, window_width == line_width)


elif not config.ON_WINDOWS and hasattr(os, 'get_terminal_size'):
    def terminal_width_impl(fd):
        config.LOGGER.debug(
            'running `os.get_terminal_size()`-based `terminal_width_impl()`'
        )
        window_width = os.get_terminal_size(fd).columns
        return make_width_info(window_width)

else:
    try:
        import termios
    except ImportError:
        termios = None

    class WinSize(ctypes.Structure):
        _fields_ = [
            ('ws_row', ctypes.c_ushort),
            ('ws_col', ctypes.c_ushort),
            ('ws_xpixel', ctypes.c_ushort),
            ('ws_ypixel', ctypes.c_ushort)
        ]

    def terminal_width_impl(fd):
        config.LOGGER.debug(
            'running `terminal_width_impl()`-fallback on a non-Windows system'
        )
        libc_path = ctypes.util.find_library('c')
        if libc_path is None or not hasattr(termios, 'TIOCGWINSZ'):
            raise OSError('unsupported platform')
        libc = ctypes.CDLL(libc_path)
        win_size = WinSize()
        libc.ioctl(fd, termios.TIOCGWINSZ, ctypes.byref(win_size))
        return make_width_info(win_size.ws_col)


def is_terminal(stream):
    """
    Return `True` if `stream` is connected to a terminal, otherwise `False`.

    Note that detection is based on the file descriptor of `stream`. Therefore,
    `stream` must implement a `.fileno()`-method which returns that file
    descriptor. If `stream` lacks this method then it is assumed to *not* be
    connected to a terminal.
    """
    if not hasattr(stream, 'fileno'):
        return False
    return os.isatty(stream.fileno())


def get_terminal_width_info(stream=config.TERMINAL_STREAM):
    """
    Return the current width of the (pseudo-)terminal connected to `stream` as
    a `TerminalWidthInfo`-object.
    """
    if not is_terminal(stream):
        raise IOError('stream must be connected to a terminal')
    return terminal_width_impl(stream.fileno())
