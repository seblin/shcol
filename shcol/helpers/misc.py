import collections
import functools
import locale
import sys

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

__all__ = [
    'StringIO', 'STRING_TYPES', 'get_decoded', 'get_sorted',
    'DefaultLocale', 'CapturedStream'
]

try:
    STRING_TYPES = (str, bytes, unicode)
except NameError:
    STRING_TYPES = (str, bytes)

def get_decoded(items, encoding):
    for item in items:
        if not isinstance(item, STRING_TYPES):
            raise TypeError('all items must be strings')
        if isinstance(item, bytes):
            item = item.decode(encoding)
        yield item

def get_sorted(items, sortkey=None):
    if sortkey is None:
        sortkey = functools.cmp_to_key(locale.strcoll)
    with DefaultLocale(locale.LC_COLLATE):
        return sorted(items, key=sortkey)


class DefaultLocale(object):
    def __init__(self, category, fail_on_locale_error=False):
        self.category = category
        self.fail_on_locale_error = fail_on_locale_error
        self.old_locale = None

    def __enter__(self):
        self.old_locale = locale.getlocale(self.category)
        try:
            locale.setlocale(self.category, '')
        except locale.Error as err:
            if self.fail_on_locale_error:
                raise err

    def __exit__(self, *unused):
        if self.old_locale is not None:
            locale.setlocale(self.category, self.old_locale)
        self.old_locale = None


class CapturedStream(object):
    def __init__(self, stream_name):
        self.stream_name = stream_name
        self.original_stream = getattr(sys, stream_name)
        self.pseudo_stream = StringIO()

    def __enter__(self):
        setattr(sys, self.stream_name, self.pseudo_stream)
        return self.pseudo_stream

    def __exit__(self, *unused):
        setattr(sys, self.stream_name, self.original_stream)
