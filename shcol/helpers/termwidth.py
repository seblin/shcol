# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014, Sebastian Linke

# Released under the Simplified BSD license
# (see LICENSE file for details).

import ctypes
import os
import platform
import sys

from .. import config

__all__ = ['get_terminal_width']

if hasattr(os, 'get_terminal_size'):
    def terminal_width_impl(fd):
        # New in Python >= 3.3
        return os.get_terminal_size(fd).columns

elif platform.system() == 'Windows':
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

    def get_terminal_width(fd=config.TERMINAL_FD):
        num_handle = -(10 + fd)
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
        pass

    class WinSize(ctypes.Structure):
        _fields_ = [
            ('ws_row', ctypes.c_ushort),
            ('ws_col', ctypes.c_ushort),
            ('ws_xpixel', ctypes.c_ushort),
            ('ws_ypixel', ctypes.c_ushort)
        ]

    def terminal_width_impl(fd):
        if not all([
            # `termios` is not available on all non-Windows systems
            'termios' in sys.modules,
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

def get_terminal_width(fd=config.TERMINAL_FD, get_width=terminal_width_impl):
    """
    Return the current width of the (pseudo-)terminal connected to the file
    descriptor `fd`.

    `get_width` should be a callable that provides a concrete implementation for
    getting the terminal's width. It is assumed to take `fd` as a parameter.
    """
    return get_width(fd)
