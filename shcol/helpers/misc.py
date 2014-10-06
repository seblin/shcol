# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014, Sebastian Linke

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
    'StringIO', 'get_decoded', 'get_sorted', 'get_filenames', 'filter_names',
    'get_dict', 'num', 'get_lines', 'get_column', 'TemporaryLocale'
]

try:
    STRING_TYPES = (str, bytes, unicode)
except NameError:
    STRING_TYPES = (str, bytes)

def get_decoded(items, encoding=config.ENCODING):
    """
    Return an iterator that yields all elements of `items` as unicode-strings.
    If `items` contains byte-strings then each of these strings is decoded to
    unicode by using the codec name specified by `encoding`. Items that are
    already unicode-strings are left unchanged. A `TypeError` is raised if a
    non-string item is encountered.
    """
    for item in items:
        if not isinstance(item, STRING_TYPES):
            raise TypeError('encountered non-string item')
        if isinstance(item, bytes):
            item = item.decode(encoding)
        yield item

def get_sorted(items, sortkey=None):
    """
    Sort given `items` in a locale-aware manner (i.e. ordering with respect to
    characters that are specific to the current locale). Note that calling this
    function temporary changes the interpreter's global locale configuration and
    thus is not thread-safe.

    Use `sortkey` if you want to provide your own key to be used for sorting.
    """
    if sortkey is None:
        sortkey = functools.cmp_to_key(locale.strcoll)
    with TemporaryLocale('', locale.LC_COLLATE):
        return sorted(items, key=sortkey)

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

def get_dict(mapping):
    """
    Return `mapping` as a dictionary. If `mapping` is already a mapping-type
    then it is returned unchanged. Otherwise it is converted to an `OrderedDict`
    to preserve the ordering of its items. Typical candidates for this function
    are sequences of 2-element tuples (defining the mapping's items). In fact,
    this function is just a shorthand for ``collections.OrderedDict(mapping)``
    but with the pre-check mentioned above.
    """
    if not isinstance(mapping, collections.Mapping):
        mapping = collections.OrderedDict(mapping)
    return mapping

def num(s):
    """
    Return string `s` converted to a number. `s` is expected to represent an
    integer >= 0. An exception is raised if conversion failed or if the result
    is a negative number.
    """
    number = int(s)
    if number < 0:
        raise ValueError('value must be non-negative')
    return number

def get_lines(source):
    """
    Return an iterator that yields all lines from `source`. Note that the
    resulting lines will not contain any trailing "\\n"-characters.
    """
    return (line.rstrip('\n') for line in source)

def get_column(column_index, source):
    """
    Return the content of a specific column linewise by using `column_index`.
    A column is defined as a sequence of non-whitespace characters. The column
    seperator is whitespace. `source` is expected to yield the lines to be
    processed.

    Note that `column_index` must be a non-negative integer. If the iterator
    encounters a line that has not enough columns for the desired `column_index`
    then `IndexError` will be thrown. Lines with no columns are ignored.
    """
    column_index = num(column_index)
    for num_line, line in enumerate(source, 1):
        columns = line.split()
        if not columns:
            continue
        if column_index >= len(columns):
            msg = 'no data for column index {} at line #{}'
            raise IndexError(msg.format(column_index, num_line))
        yield columns[column_index]


class TemporaryLocale(object):
    """
    A class to temporary change the interpreter's locale configuration.
    """
    def __init__(
        self, locale_name, category=locale.LC_ALL, fail_on_locale_error=False
    ):
        """
        Create a new `TemporaryLocale`.

        `locale_name` defines the name of the locale to be temporary used. This
        name has the same meaning as it would be directly passed to the stdlib's
        `locale.setlocale`-function.

        `category` defines the locale's category. It should be one of the
        `LC_*`-constants defined in the stdlib's `locale`-module.

        If `fail_on_locale_error` is `True` then a `locale.Error`, that might
        occur when setting the temporary locale, will be raised. Otherwise,
        this exception is silently ignored. However, a `locale.Error` will
        always let the locale setting remain in its old state (i.e. temporary
        locale was not set), no matter if it was ignored or not.
        """
        self.locale_name = locale_name
        self.category = category
        self.fail_on_locale_error = fail_on_locale_error
        self.original_locale = locale.getlocale(category)

    def set(self):
        """
        Set the temporary locale. If this was successful then the resulting
        locale string is returned.
        """
        try:
            return locale.setlocale(self.category, self.locale_name)
        except locale.Error as err:
            if self.fail_on_locale_error:
                raise err

    def unset(self):
        """
        Unset the temporary locale and restore the old locale settings.
        """
        locale.setlocale(self.category, self.original_locale)

    def __enter__(self):
        return self.set()

    def __exit__(self, *unused):
        self.unset()
