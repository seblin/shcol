# -*- coding: utf-8 -*-
# Copyright (c) 2013-2015, Sebastian Linke

# Released under the Simplified BSD license
# (see LICENSE file for details).

"""
Detect terminal width on different platforms.
"""

import ctypes
import os

from .. import config

__all__ = ['get_terminal_width']

if hasattr(os, 'get_terminal_size'):
    def terminal_width_impl(fd):
        # New in Python >= 3.3
        return os.get_terminal_size(fd).columns

elif config.ON_WINDOWS:
    import ctypes.wintypes

    class ConsoleScreenBufferInfo(ctypes.Structure):
        _fields_ = [
            ('dwSize', ctypes.wintypes._COORD),
            ('dwCursorPosition', ctypes.wintypes._COORD),
            ('wAttributes', ctypes.wintypes.WORD),
            ('srWindow', ctypes.wintypes.SMALL_RECT),
            ('dwMaximumWindowSize', ctypes.wintypes._COORD)
        ]
        _pack_ = 2

    GetStdHandle = ctypes.windll.kernel32.GetStdHandle
    GetStdHandle.restype = ctypes.wintypes.HANDLE
    GetStdHandle.argtypes = [ctypes.wintypes.DWORD]

    GetConsoleScreenBufferInfo = (
        ctypes.windll.kernel32.GetConsoleScreenBufferInfo
    )
    GetConsoleScreenBufferInfo.restype = ctypes.wintypes.BOOL
    GetConsoleScreenBufferInfo.argtypes = [
        ctypes.wintypes.HANDLE,
        ctypes.POINTER(ConsoleScreenBufferInfo),
    ]

    def terminal_width_impl(fd):
        num_handle = (-10, -11, -12)[fd]
        handle = GetStdHandle(num_handle)
        csbi = ctypes.pointer(ConsoleScreenBufferInfo())
        GetConsoleScreenBufferInfo(handle, csbi)
        window = csbi.contents.srWindow
        return window.Right - window.Left + 1

else:
    try:
        import fcntl
        import termios
    except ImportError:
        import_ok = False
    else:
        import_ok = True

    class WinSize(ctypes.Structure):
        _fields_ = [
            ('ws_row', ctypes.c_ushort),
            ('ws_col', ctypes.c_ushort),
            ('ws_xpixel', ctypes.c_ushort),
            ('ws_ypixel', ctypes.c_ushort)
        ]

    def terminal_width_impl(fd):
        if not all([
            # some modules might not be available on all non-Windows systems
            import_ok,
            # `TIOCGWINSZ` must be defined
            hasattr(termios, 'TIOCGWINSZ'),
            # Python-2.7-compatible `pypy`-interpreter lacks this
            hasattr(ctypes.Structure, 'from_buffer_copy')
        ]):
            raise OSError('unsupported platform')
        result = fcntl.ioctl(
            fd, termios.TIOCGWINSZ, ctypes.sizeof(WinSize) * '\0'
        )
        return WinSize.from_buffer_copy(result).ws_col


def get_terminal_width(
    fd=config.TERMINAL_FD, fallback_width=config.LINE_WIDTH_FALLBACK
):
    """
    Return the current width of the (pseudo-)terminal connected to the file
    descriptor `fd`.

    `fallback_width` is returned when getting the terminal width failed with
    `IOError` or `OSError`.
    """
    try:
        return terminal_width_impl(fd)
    except (IOError, OSError):
        return fallback_width
