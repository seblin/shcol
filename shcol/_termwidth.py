import ctypes
import os
import platform
import sys

if hasattr(os, 'get_terminal_size'):
    def get_terminal_width(fd):
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

    def get_terminal_width(fd):
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

    def get_terminal_width(fd):
        if not 'termios' in sys.modules or not hasattr(termios, 'TIOCGWINSZ'):
            raise IOError('unsupported platform')
        result = fcntl.ioctl(
            fd, termios.TIOCGWINSZ, ctypes.sizeof(WinSize) * '\0'
        )
        return WinSize.from_buffer_copy(result).ws_col
