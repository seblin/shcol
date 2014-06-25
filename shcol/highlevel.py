from __future__ import print_function

import collections
import glob
import os

from .core import columnize

__all__ = [
    'print_columnized', 'print_columnized_mapping', 'print_attrs', 'print_files'
]

def print_columnized(items, *args, **kwargs):
    """
    Shortcut to show the columnized `items` on standard output.
    Takes the same arguments as `columnize()`.
    """
    print(columnize(items, *args, **kwargs))

def print_columnized_mapping(items, *args, **kwargs):
    mapping = collections.OrderedDict(items)
    print_columnized(mapping, *args, **kwargs)

def print_attrs(obj):
    """
    Similar to the `dir()`-builtin but sort the resulting names
    and print them columnized to stdout.
    """
    print_columnized(dir(obj), sort_items=True)

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

def print_files(path='.', hide_dotted=False):
    """
    Columnize filenames according to given `path` and print them
    to stdout.

    `hide_dotted` defines whether to exclude filenames starting
    with a ".".

    Note that this function does shell-like expansion of symbols
    such as "*", "?" or even "~" (user's home).
    """
    filenames = _get_files(path, hide_dotted)
    print_columnized(filenames, sort_items=True)
