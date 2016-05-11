# -*- coding: utf-8 -*-
# Copyright (c) 2013-2016, Sebastian Linke

# Released under the Simplified BSD license
# (see LICENSE file for details).

import fnmatch
import functools
import glob
import locale
import os
import re

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from .. import config

__all__ = [
    'StringIO', 'get_strings', 'get_sorted', 'make_unique', 'get_filenames',
    'filter_names', 'num', 'get_lines', 'get_column', 'make_object_repr'
]

def get_strings(items, encoding=config.ENCODING):
    """
    Convert `items` to Unicode strings and return the result as an iterator.

    `encoding` defines the name of the encoding to be used for decoding when
    an item is a byte string.
    """
    for item in items:
        if isinstance(item, bytes):
            yield item.decode(encoding)
        else:
            yield config.UNICODE_TYPE(item)

def get_sorted(items):
    """
    Sort `items` with respect to characters that are specific to the current
    locale setting and return the result as a new list.

    Note that this function temporary changes the interpreter's global locale
    configuration if no specific locale was set before. This is done in order
    to achieve sorting based on the system's default locale as a fallback. The
    "unset locale"-state will then be restored right after sorting was done.
    """
    unset_locale = (None, None)
    old_locale = locale.getlocale(locale.LC_COLLATE)
    if old_locale == unset_locale:
        try:
            default_locale = locale.setlocale(locale.LC_COLLATE, '')
        except locale.Error as err:
            # Very unlikely to occur, but just to be safe.
            msg = 'setting default locale failed with locale.Error: {}'
            config.LOGGER.debug(msg.format(err))
        else:
            msg = 'temporary switched to default locale: {}'
            config.LOGGER.debug(msg.format(default_locale))
    sortkey = functools.cmp_to_key(locale.strcoll)
    sorted_items = sorted(items, key=sortkey)
    if old_locale == unset_locale:
        locale.setlocale(locale.LC_COLLATE, unset_locale)
    return sorted_items

def make_unique(items):
    """
    Return an iterator based on `items` that only yields the first occurrence of
    an item. Any further occurrences of an item are ignored.

    Note that in contrast to a `set()` this function will preserve the original
    order of the given items.
    """
    seen = set()
    for item in items:
        if item not in seen:
            seen.add(item)
            yield item

def get_filenames(path=os.curdir):
    """
    Return an iterator of the filenames in `path`. If this function could not
    retrieve any filename due to access errors then the iterator will be empty
    (i.e. yielding no items).

    Note that shell-like globbing is performed if `path` contains wildcard
    symbols such as "*" or "?". The function will then return all names that
    match the given pattern instead of their directory contents. If you need the
    contents then you should put the platform's path separator at the end of
    your pattern. In other words (on Windows):

    r'Python27'   => Content of "Python27"-folder
    r'Py*'        => Names starting with "Py" (e.g. "Python27", "Python34", ...)
    r'Py*\\'      => Contents of directories starting with "Py"
    r'Py*\*.txt'  => E.g. all text files in all Python folders

    To make life easier, you are free to use alternative path separators if
    they are supported by your platform (e.g. "/" instead of "\" on Windows).
    Additionally, the "~"-symbol will be expanded to the user's home directory.
    """
    path = os.path.expanduser(os.path.expandvars(path))
    if os.altsep is not None:
        path = path.replace(os.altsep, os.sep)
    if not glob.has_magic(path) or path.endswith(os.sep):
        path = os.path.join(path, '*')
    filenames = (fn.rstrip(os.sep) for fn in glob.iglob(path))
    if not glob.has_magic(os.path.dirname(path)):
        filenames = (os.path.basename(fn) for fn in filenames)
    return filenames

def filter_names(source, pattern):
    """
    Return all names that match the given pattern.

    `source` should be an iterator with the names to be processed.

    `pattern` is meant to be an expression that is free to make use of
    shell-like file matching mechanisms (e.g. "x*" to match all names
    starting with "x").
    """
    pattern = re.compile(fnmatch.translate(pattern))
    return (name for name in source if pattern.match(name))

def num(value, allow_none=False, allow_zero=False):
    """
    Return `value` converted to an `int`-object.

    `value` should represent a non-negative integer. It must be convertible for
    the built-in `int()`-function. An error is thrown if the conversion failed
    or if the result of the conversion is a negative number.

    Note that no conversion is made if `value` is `None` and `allow_none` is
    `True`. In that case the function just returns `None`.

    If `value` is zero and `allow_zero` is `False` then the function will fail.
    """
    if allow_none and value is None:
        return None
    value_error = False
    try:
        number = int(value)
    except ValueError:
        value_error = True
    if value_error or number < 0:
        raise ValueError('value must be a non-negative integer')
    if value == 0 and not allow_zero:
        raise ValueError('value must be non-zero')
    return number

def get_lines(source, chars=None, skip_emtpy=True):
    """
    Return an iterator that yields all lines from `source`.

    `chars` defines the characters to be stripped from the end of each line.
    If `None` is used then all trailing whitespace characters are stripped.

    Setting `skip_empty` to `True` means that all lines, that have no content
    after stripping was done (=empty strings), are *not* yielded.
    """
    for line in source:
        line = line.rstrip(chars)
        if line or not skip_emtpy:
            yield line

def get_column(column_index, source, sep=None):
    """
    Return the content of a specific column.

    `column_index` defines the index of the column to be extracted. It must be
    an integer >= 0.

    `source` is expected to be an iterator yielding the lines to be processed.
    The resulting column will be based on these lines.

    `sep` should be a string that defines the separator between each column. If
    `None` is used instead then the separator is whitespace.

    If this function encounters a line having not enough columns to fulfill the
    given column index then it will fail by throwing `IndexError`.
    """
    column_index = num(column_index, allow_zero=True)
    maxsplit = column_index + 1
    for num_line, line in enumerate(source):
        columns = line.split(sep, maxsplit)
        if column_index >= len(columns):
            msg = 'no data for column index {} at line index {}'
            raise IndexError(msg.format(column_index, num_line))
        yield columns[column_index]

def make_object_repr(obj, attr_names):
    """
    Return a string that contains the type of `obj` and a selection of its
    attribute names with their corresponding values based on given `attr_names`.
    The result may be used as an object's `__repr__()`-string.
    """
    attr_string = ', '.join(
        '{}={!r}'.format(name, getattr(obj, name)) for name in attr_names
    )
    return '{}({})'.format(type(obj).__name__, attr_string)
