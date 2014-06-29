from __future__ import print_function

import collections

from .core import columnize
from . import helpers

__all__ = [
    'print_columnized', 'print_columnized_mapping', 'print_attrs', 'print_files'
]

def print_columnized(items, *args, **kwargs):
    """
    Shortcut to show the columnized `items` on standard output.
    Takes the same arguments as `columnize()`.
    """
    print(columnize(items, *args, **kwargs))

def print_columnized_mapping(items, **kwargs):
    print_columnized(helpers.get_dict(mapping), **kwargs)

def print_attrs(obj, **kwargs):
    """
    Similar to the `dir()`-builtin but sort the resulting names
    and print them columnized to stdout.
    """
    print_columnized(dir(obj), sort_items=True, **kwargs)

def print_files(path='.', hide_dotted=False, **kwargs):
    """
    Columnize filenames according to given `path` and print them
    to stdout.

    `hide_dotted` defines whether to exclude filenames starting
    with a ".".

    Note that this function does shell-like expansion of symbols
    such as "*", "?" or even "~" (user's home).
    """
    filenames = helpers.get_files(path, hide_dotted)
    print_columnized(filenames, sort_items=True, **kwargs)
