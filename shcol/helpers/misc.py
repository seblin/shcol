import collections
import functools
import locale
import os
import sys

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

__all__ = [
    'StringIO', 'STRING_TYPES', 'get_decoded', 'get_sorted', 'DefaultLocale',
    'get_files', 'get_dict', 'num', 'read_lines', 'exit_with_failure',
    'CapturedStream'
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


def get_files(path, hide_dotted):
    """
    Return a sequence of the filenames in `path`. Note that this function does
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
        filenames = [fn for fn in filenames if not fn.startswith('.')]
    return filenames


def get_dict(mapping):
    """
    Return `mapping` as a dictionary. If mapping is already a `Mapping`-type
    then it is returned unchanged. Otherwise it is converted to an `OrderedDict`
    to preserve the ordering of its items. Typical candidates for this function
    are sequences of 2-element tuples. In fact, this is just a shorthand for
    `collections.OrderedDict(mapping)` but with the pre-check mentioned before.
    """
    if isinstance(mapping, collections.Mapping):
        return mapping
    return collections.OrderedDict(mapping)


def num(s):
    """
    Return string `s` converted to a number. `s` is expected to represent an
    integer >= 0. An exception is raised if conversion failed or if the result
    is a negative number.
    """
    number = int(s)
    if number < 0:
        raise ValueError('number must be non-negative')
    return number

def read_lines(stream, column_index=None):
    """
    Return an iterator that yields all lines from `stream` removing any trailing
    "\n"-characters per line. `column_index` may be used to restrict reading to
    specific column per line. Note that the index value is interpreted as an
    ordinary Python index. A column is defined as a sequence of non-whitespace
    characters. The column seperator is whitespace.
    """
    lines = (line.rstrip('\n') for line in stream)
    if column_index is not None:
        lines = (line.split()[column_index] for line in lines)
    return lines


def exit_with_failure(msg=None):
    """
    Exit the application with exit code 1. If `msg` is given then its text is
    printed to stderr.
    """
    if msg is not None:
        sys.stderr.write(msg + '\n')
    sys.exit(1)


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
