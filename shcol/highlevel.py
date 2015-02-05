# -*- coding: utf-8 -*-
# Copyright (c) 2013-2015, Sebastian Linke

# Released under the Simplified BSD license
# (see LICENSE file for details).

"""
Highlevel functions to support some cases where columnizing can be useful.
"""

from __future__ import print_function

from . import config, core, helpers

__all__ = [
    'print_columnized', 'print_columnized_mapping', 'print_attr_names',
    'print_filenames'
]

def print_columnized(items, output_stream=config.OUTPUT_STREAM, **kwargs):
    """
    Shorthand for writing columnized `items` to `output_stream`. Additional
    keyword-arguments are passed as is to the underlying `columnize()`-function
    and are interpreted there.
    """
    result = core.columnize(items, **kwargs)
    print(result, file=output_stream)

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

def print_attr_names(obj, pattern=None, **kwargs):
    """
    Like `print_columnized()` but columnizes the attribute names of `obj`.

    If `pattern` is not `None` then the resulting names are filtered by using
    the expression defined by `pattern`. This works like matching filenames in
    a shell (e.g. using "get_*" will only columnize attribute names starting
    with "get_").
    """
    names = dir(obj)
    if pattern is not None:
        names = helpers.filter_names(names, pattern)
    print_columnized(names, sort_items=True, **kwargs)

def print_filenames(path='.', hide_dotted=False, **kwargs):
    """
    Like `print_columnized()` but columnizes the filenames living in given
    `path`. If `hide_dotted` is `True` then all filenames starting with a "."
    are excluded from the result. Note that this function does shell-like
    expansion of symbols such as "*", "?" or even "~" (user's home).
    """
    filenames = helpers.get_filenames(path, hide_dotted)
    print_columnized(filenames, sort_items=True, **kwargs)
