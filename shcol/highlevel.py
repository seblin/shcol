from __future__ import print_function
from .core import columnize
import glob
import os

__all__ = ['show_attrs', 'show_files']

def show_attrs(obj):
    """
    Similar to the `dir()`-builtin but sort the resulting names
    and print them columnized to stdout.
    """
    print(columnize(dir(obj), sort_items=True))

def _get_files(path, hide_dotted):
    path = os.path.expanduser(os.path.expandvars(path))
    try:
        filenames = os.listdir(path)
    except OSError as err:
        filenames = glob.glob(path)
        if not filenames:
            raise err
    if hide_dotted:
        filenames = [fn for fn in filenames if not fn.startswith('.')]
    return filenames

def show_files(path='.', hide_dotted=False):
    """
    Columnize filenames according to given `path` and print them
    to stdout.

    Note that this function does shell-like expansion of symbols
    such as "*", "?" or even "~" (user's home).
    """
    filenames = _get_files(path, hide_dotted)
    print(columnize(filenames, sort_items=True))
