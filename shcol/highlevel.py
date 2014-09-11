# -*- coding: utf-8 -*-
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

def print_columnized(items, print_stream=config.PRINT_STREAM, **kwargs):
    """
    Shortcut for writing columnized `items` to `print_stream` (standard output
    by default). Additional keyword-arguments are passed as is to the underlying
    `columnize()`-function and are interpreted there.
    """
    result = core.columnize(items, **kwargs)
    print(result, file=print_stream)

def print_columnized_mapping(items, **kwargs):
    """
    Like `print_columnized()` but expects `items` to be given as a mapping.
    
    Alternatively, `items` may be given as an iterable of 2-element tuples.
    In that case each tuple will be interpreted as a "key-value pair" just 
    like it would have been provided by a mapping.
    
    In both cases a string with exactly two columns (i.e. one for the keys
    and one for the values) is returned. Note that an exception will occur
    if the result would exceed the allowed line width.
    """
    print_columnized(helpers.get_dict(items), **kwargs)

def print_attrs(obj, **kwargs):
    """
    Similar to the `dir()`-builtin but sort the resulting names
    and print them columnized to standard output.
    """
    print_columnized(dir(obj), sort_items=True, **kwargs)

def print_filenames(path='.', hide_dotted=False, **kwargs):
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
