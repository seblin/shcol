# -*- coding: utf-8 -*-
# Copyright (c) 2013-2015, Sebastian Linke

# Released under the Simplified BSD license
# (see LICENSE file for details).

import collections
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
    'StringIO', 'get_decoded', 'get_sorted', 'make_unique', 'get_filenames',
    'filter_names', 'is_mapping', 'get_dict', 'num', 'get_lines', 'get_column'
]

def get_decoded(items, encoding=config.ENCODING):
    """
    Decode given `items` and return the result as an iterator.

    `encoding` defines the name of the encoding to be used. It is passed to each
    item's `.decode()`-method.

    Note that if an item does not provide a `.decode()`-method or if decoding
    throws a `UnicodeEncodeError` (as on Python 2.x) then the item is left
    unchanged. Any other exception during decoding an item will cause an error.
    """
    for item in items:
        try:
            yield item.decode(encoding)
        except (AttributeError, UnicodeEncodeError):
            yield item


def get_sorted(items, locale_name='', strict=False):
    """
    Sort `items` with respect to characters that are specific to the given
    locale. The result will be returned as a new list.

    `locale_name` defines the locale to be used. It has the same meaning as if
    it would have been passed to the stdlib's `locale.setlocale()`-function. If
    given as an empty string (the default) then the system's default locale will
    be used.

    Use `strict` to decide what to do if setting the locale failed with a
    `locale.Error`. `True` means that the function will fail by throwing the
    error. `False` means that the error is ignored and sorting is done
    locale-independent by simply calling `sorted(items)`.

    Note that this function temporary changes the interpreter's global locale
    configuration. It does this by storing the current locale and then setting
    the given locale name. Then the items are sorted and after that it will set
    the stored locale again. This function is not thread-safe.
    """
    locale_name_was_set = False
    old_locale = locale.getlocale(locale.LC_COLLATE)
    sortkey = functools.cmp_to_key(locale.strcoll)
    try:
        # `old_locale` might be invalid (at least on Windows)
        # => try to set it before doing the "real" switch
        locale.setlocale(locale.LC_COLLATE, old_locale)
        locale.setlocale(locale.LC_COLLATE, locale_name)
        locale_name_was_set = True
        result = sorted(items, key=sortkey)
    except locale.Error:
        if strict:
            raise
        result = sorted(items)
    finally:
        if locale_name_was_set:
            # this would fail otherwise
            locale.setlocale(locale.LC_COLLATE, old_locale)
    return result

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

def get_filenames(path='.', hide_dotted=False):
    """
    Return an iterator of the filenames in `path`. Note that this function does
    shell-like expansion of symbols such as "*", "?" or even "~" (user's home).

    `hide_dotted` defines whether to exclude filenames starting with a ".".
    """
    path = os.path.expanduser(os.path.expandvars(path))
    try:
        filenames = os.listdir(path)
    except OSError as err:
        filenames = glob.glob(path)
        if not filenames:
            raise err
    if hide_dotted:
        filenames = (fn for fn in filenames if not fn.startswith('.'))
    return iter(filenames)

def filter_names(source, pattern):
    """
    Yield all names that match the given pattern.

    `source` is expected to yield the names to be processed.

    `pattern` is meant to be an expression that is free to make use of
    shell-like file matching mechanisms (e.g. "x*" to match all names
    starting with "x").
    """
    pattern = re.compile(fnmatch.translate(pattern))
    for name in source:
        match = pattern.match(name)
        if match is not None:
            yield match.group(0)

def is_mapping(obj):
    """
    Return `True` if `obj` is considered to be a mapping. Return `False`
    otherwise. Note that this function does a "duck-type" check. It only
    checks the presence of a `keys`- and a `values`-attribute.
    """
    return hasattr(obj, 'keys') and hasattr(obj, 'values')

def get_dict(mapping):
    """
    Return `mapping` as a dictionary. If `mapping` is already a mapping-type
    then it is returned unchanged. Otherwise it is converted to an `OrderedDict`
    to preserve the ordering of its items. Typical candidates for this function
    are sequences of 2-element tuples (defining the mapping's items). In fact,
    this function is just a shorthand for ``collections.OrderedDict(mapping)``
    but with the pre-check mentioned above.
    """
    if not is_mapping(mapping):
        mapping = collections.OrderedDict(mapping)
    return mapping

def num(value, allow_none=False):
    """
    Return `value` converted to an `int`-object. `value` should represent an
    integer >= 0. It may be any kind of object that supports conversion when
    passed to the built-in `int()`-function. An exception will be raised if the
    conversion failed or if the result of the conversion is a negative number.

    Note that `value` may be `None` if `allow_none` is `True`. In that case no
    conversion is made and the function just returns `None`. Otherwise, passing
    `None` as the `value`-parameter will raise a `TypeError`.
    """
    if allow_none and value is None:
        return None
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise TypeError('value should represent an integer')
    if number < 0:
        raise ValueError('value must be non-negative')
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
    column_index = num(column_index)
    maxsplit = column_index + 1
    for num_line, line in enumerate(source):
        columns = line.split(sep, maxsplit)
        if column_index >= len(columns):
            msg = 'no data for column index {} at line index {}'
            raise IndexError(msg.format(column_index, num_line))
        yield columns[column_index]
