# -*- coding: utf-8 -*
# Copyright (c) 2013-2014, Sebastian Linke

# Released under the Simplified BSD license 
# (see LICENSE file for details).

from __future__ import print_function

import collections

from . import config, core, helpers

__all__ = [
    'print_columnized', 'print_columnized_mapping', 'print_attrs',
    'print_filenames'
]

def print_columnized(items, *args, **kwargs):
    """
    Shortcut to show the columnized `items` on standard output.
    Takes the same arguments as `columnize()`.
    """
    result = core.columnize(items, *args, **kwargs)
    print(result, file=config.PRINT_STREAM)

def print_columnized_mapping(mapping, **kwargs):
    print_columnized(helpers.get_dict(mapping), **kwargs)

def print_attrs(obj, **kwargs):
    """
    Similar to the `dir()`-builtin but sort the resulting names
    and print them columnized to standard output.
    """
    print_columnized(dir(obj), sort_items=True, **kwargs)

def print_filenames(path='.', hide_dotted=config.HIDE_DOTTED, **kwargs):
    """
    Columnize filenames according to given `path` and print them
    to standard output.

    `hide_dotted` defines whether to exclude filenames starting
    with a "." from the result.

    Note that this function does shell-like expansion of symbols
    such as "*", "?" or even "~" (user's home).
    """
    filenames = helpers.get_filenames(path, hide_dotted)
    print_columnized(filenames, sort_items=True, **kwargs)
