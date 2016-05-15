# -*- coding: utf-8 -*-
# Copyright (c) 2013-2016, Sebastian Linke

# Released under the Simplified BSD license
# (see LICENSE file for details).

"""
Classes and functions providing the core functionality of `shcol`.
"""

import collections

from .. import config, helpers
from . import formatters

__all__ = ['formatters', 'columnize']

def columnize(
    items, spacing=config.SPACING, line_width=config.LINE_WIDTH,
    pattern=None, make_unique=config.MAKE_UNIQUE, sort_items=config.SORT_ITEMS,
    output_stream=config.TERMINAL_STREAM
):
    """
    Return a columnized string based on `items`. Note that `items` can be a
    sequence or a dictionary. In case of being a dictionary the result will be
    a string with two columns (i.e. one for the keys and one for the values).
    In case of a sequence the resulting number of columns is calculated by the
    underlying algorithm. The result is then similar to the output generated by
    the Unix-tool `ls`.

    `spacing` should be a non-negative integer defining the number of blank
    characters between two columns.

    `line_width` should be a non-negative integer defining the maximal amount
    of characters that fit in one line. If this is `None` then the function
    tries to detect the width automatically.

    If `pattern` is not `None` then it is meant to be an expression that is
    free to make use of shell-like file matching mechanisms for matching a
    subset of `items` (e.g. "x*" to match all items starting with "x").

    If `make_unique` is `True` then only the first occurrence of an item is
    processed and any other occurrences of that item are ignored.

    If `sort_items` is `True`, then a locale-aware sorted version of `items`
    is used to generate the columnized output. Note that enabling sorting is not
    thread-safe because it temporarily changes the interpreter's global `locale`
    configuration.

     `output_stream` defines the stream where the result should be written to.
    """
    if make_unique and not isinstance(items, collections.Mapping):
        items = helpers.make_unique(items)
    formatter_class = formatters.find_formatter(items)
    if line_width is None:
        try:
            formatter = formatter_class.for_terminal(output_stream, spacing)
        except (IOError, OSError):
            raise OSError('unable to detect line width')
    else:
        formatter = formatter_class.for_line_config(spacing, line_width)
    items = (str(item) for item in items)
    return formatter.format(items, pattern=pattern, sort_items=sort_items)
