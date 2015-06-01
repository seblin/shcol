# -*- coding: utf-8 -*-
# Copyright (c) 2013-2015, Sebastian Linke

# Released under the Simplified BSD license
# (see LICENSE file for details).

"""
Highlevel functions to support some cases where columnizing can be useful.
"""

from __future__ import print_function

from . import config, core, helpers

__all__ = ['print_columnized', 'print_attr_names', 'print_filenames']

def print_columnized(items, output_stream=config.TERMINAL_STREAM, **options):
    """
    Shorthand for writing columnized `items` to `output_stream`.

    `items` can be a sequence or a dictionary. In case of being a dictionary
    the result will be a string with two columns (i.e. one for the keys and one
    for the values). In case of a sequence the resulting number of columns is
    calculated by the underlying algorithm.

    `output_stream` should be a file-like object that provides at least a
    `.write()`-method.

    Additional `options` are passed as-is to the `columnize()`-function and are
    interpreted there. See `columnize()`-documentation for details.
    """
    result = core.columnize(items, output_stream=output_stream, **options)
    print(result, file=output_stream)

def print_attr_names(obj, **options):
    """
    Like `print_columnized()` but columnizes the attribute names of `obj`.
    """
    print_columnized(dir(obj), sort_items=True, **options)

def print_filenames(path='.', hide_dotted=False, **options):
    """
    Like `print_columnized()` but columnizes the filenames living in given
    `path`. If `hide_dotted` is `True` then all filenames starting with a "."
    are excluded from the result. Note that this function does shell-like
    expansion of symbols such as "*", "?" or even "~" (user's home).
    """
    filenames = helpers.get_filenames(path, hide_dotted)
    print_columnized(filenames, sort_items=True, **options)
