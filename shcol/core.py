from __future__ import unicode_literals
import collections
import os
import sys

from . import helpers

LineProperties = collections.namedtuple(
    'LineProperties', 'column_widths, spacing, num_lines'
)

def columnize(items, spacing=2, max_line_width=None, sort_items=False):
    """
    Return a columnized string based on `items`. The result is similar to
    the output generated by tools like `ls`.

    `spacing` defines the number of blank characters between two columns.

    `max_line_width` defines the maximal amount of characters per line. If
    this is `None` then the terminal's width is used.

    If `sort_items` is `True`, then a locale-aware sorted version of `items`
    is used to generate the columnized output.

    Note that enabling `sort_items` may temporary change the interpreter's
    global locale configuration and thus is not thread-safe (which might be
    relevant in some cases). Leave this option disabled (the default) if you
    want to avoid this.
    """
    if max_line_width is None:
        try:
            calculator = ColumnWidthCalculator.for_terminal(spacing)
        except (IOError, OSError):
            # failed to get terminal width -> use calculator's default value
            calculator = ColumnWidthCalculator(spacing)
    else:
        calculator = ColumnWidthCalculator(spacing, max_line_width)
    formatter = build_formatter(type(items), calculator, sort_items)
    return formatter.format(items)


class ColumnWidthCalculator(object):
    """
    A class with capabilities to calculate the widths for an unknown number
    of columns based on a given sequence of strings.
    """
    def __init__(self, spacing=2, max_line_width=80, max_columns=None):
        """
        Initialize the calculator. `spacing` defines the number of blanks
        between two columns. `max_line_width` is the maximal amount of
        characters that a line may consume.
        """
        self.spacing = spacing
        self.max_line_width = max_line_width
        self.max_columns = max_columns

    def get_line_properties(self, items):
        """
        Return a namedtuple containing meaningful properties that may be used
        to format `items` as a columnized string.

        The members of the tuple are: `column_widths`, `spacing`, `num_lines`.
        """
        if isinstance(items, collections.Mapping):
            return self._get_props_for_mapping(items)
        item_widths = [len(item) for item in items]
        column_widths, num_lines = self.calculate_columns(item_widths)
        return LineProperties(column_widths, self.spacing, num_lines)

    def _get_props_for_mapping(self, mapping):
        if not mapping:
            return LineProperties([], self.spacing, 0)
        key_widths = map(len, mapping.keys())
        value_widths = map(len, mapping.values())
        column_widths = [max(key_widths), max(value_widths)]
        if not self.fits_in_line(column_widths):
            column_widths[1] = self.max_line_width - column_widths[0] - spacing
        return LineProperties(column_widths, self.spacing, len(mapping))

    def calculate_columns(self, item_widths):
        """
        Calculate column widths based on `item_widths`, expecting `item_widths`
        to be a sequence of non-negative integers that represent the length of
        each corresponding string. The result is returned as a tuple consisting
        of two elements: A sequence of calculated column widths and the number
        of lines needed to display all items when using that information to do
        columnized formatting.

        Note that this instance's `.max_line_width` and `.spacing` attributes
        are taken into account when calculation is done. However, the column
        widths of the resulting tuple will *not* include that spacing.
        """
        max_columns = self.calculate_max_columns(item_widths)
        if max_columns == 0:
            return [], 0
        num_items = len(item_widths)
        for num_columns in range(max_columns, 0, -1):
            num_lines = num_items // num_columns + bool(num_items % num_columns)
            if not self.fits_in_line(item_widths[::num_lines]):
                # give up early if first items
                # of columns do not fit in line
                continue
            column_widths = [
                max(item_widths[i : i + num_lines])
                for i in range(0, num_items, num_lines)
            ]
            if self.fits_in_line(column_widths):
                return column_widths, num_lines
        return [self.max_line_width], len(item_widths)

    def calculate_max_columns(self, item_widths):
        """
        Return the number of columns that is guaranteed not to be exceeded when
        `item_widths` are columnized. Return `0` if `item_widths` is empty.

        This is meant to be used as an upper bound on which the real calculation
        of resulting column widths may be based on. Using this value can save a
        remarkable number of iterations depending on the way how column width
        calculation is implemented.
        """
        num_items = len(item_widths)
        if num_items <= 1:
            return num_items
        smallest_item, widest_item = min(item_widths), max(item_widths)
        if widest_item >= self.max_line_width:
            return 1
        remaining_width = self.max_line_width - widest_item
        min_width = self.spacing + smallest_item
        possible_columns = 1 + remaining_width // min_width
        return min(num_items, possible_columns)

    def fits_in_line(self, column_widths):
        """
        Summarize the values of given `column_widths`, add `.spacing` between
        each column and then check whether it exceeds `.max_line_width`. Return
        `True` if the result does *not* exceed the allowed line width. Return
        `False` otherwise.
        """
        total = sum(column_widths) + (len(column_widths) - 1) * self.spacing
        return total <= self.max_line_width

    @classmethod
    def for_terminal(cls, spacing=2, stream=None):
        """
        Return a new `ColumnWidthCalculator` based on given `stream` where
        `stream` must be a file-object connected to a terminal. If `stream` is
        `None` then `sys.__stdout__` is used instead.

        `spacing` defines the number of blanks between two columns and is used
        by the resulting calculator.

        The calculator's line width will equal to the line width of the given
        terminal-stream. But note that the calculator's line width is *not*
        updated if subsequent changes of the terminal size occur after
        initialization of the calculator.
        """
        if stream is None:
            stream = sys.__stdout__
        width = helpers.get_terminal_width(stream.fileno())
        return cls(spacing, width)


class SequenceFormatter(object):
    """
    A class to do columnized formatting on a given sequence of strings.
    """
    def __init__(
        self, calculator, linesep=os.linesep, encoding='utf-8', sort_items=False
    ):
        """
        Initialize the formatter. 

        `calculator` will be used to determine the width of each column when
        columnized string formatting is done. It should be a class instance
        that implements a `.get_properties()` method in a similar way as
        `ColumnWidthCalculator` does.

        `linesep` defines the character(s) used to start a new line.

        `encoding` will be used when formatting byte-strings. These strings are
        decoded to unicode-strings by using the given `encoding`.
        """
        self.calculator = calculator
        self.linesep = linesep
        self.encoding = encoding
        self.sort_items = sort_items

    def format(self, items):
        """
        Return a columnized string based on `items` where `items` is expected to
        be an iterator of strings or bytes. Note that items that are bytes will
        be converted to a string by using the codec specified in this instance's
        `encoding`-attribute.
        """
        if self.sort_items:
            items = self.get_sorted(items)
        decoded_items = self.get_decoded(items)
        lines = self.make_lines(decoded_items)
        return self.linesep.join(lines)

    @staticmethod
    def get_sorted(items):
        return helpers.get_sorted(items)

    def get_decoded(self, items):
        return list(helpers.get_decoded(items, self.encoding))

    def make_lines(self, items):
        """
        Return columnized lines for `items` yielded by an iterator where `items`
        is expected to be a sequence of strings. Note that this method does not
        append newline characters to the end of the resulting lines.
        """
        props = self.get_line_properties(items)
        line_chunks = self.make_line_chunks(items, props)
        template = self.make_line_template(props)
        for chunk in line_chunks:
            try:
                yield template % chunk
            except TypeError:
                # cached template does not match current chunk length
                # -> regenerate and try again
                template = self.make_line_template(props, len(chunk))
                yield template % chunk

    def get_line_properties(self, items):
        return self.calculator.get_line_properties(items)

    @staticmethod
    def make_line_chunks(items, props):
        return [
            tuple(items[i::props.num_lines]) for i in range(props.num_lines)
        ]

    def make_line_template(self, props, num=None):
        """
        Return a string meant to be used as a formatting template for *one* line
        of columnized output. The template will be suitable for old-style string
        formatting ('%s' % my_string). 

        `props` is expected to be a `LineProperties`-instance as it is defined
        in this module. Appropriated format specifiers are generated based on
        the information of `props.column_widths`. In the resulting template the
        specifiers are joined by using a separator with a `props.spacing` number
        of blank characters.
        """
        widths = props.column_widths[:num]
        if not widths:
            return ''
        parts = [self.get_padded_template(width) for width in widths[:-1]]
        parts.append(self.get_unpadded_template(widths[-1]))
        return (props.spacing * ' ').join(parts)

    @staticmethod
    def get_padded_template(width):
        """
        Return a column template suitable for string formatting with exactly
        one string argument (e.g. template % mystring).

        The template is guaranteed to produce results which are always exactly
        `width` characters long. If a string smaller than the given `width` is
        passed to the template then the result will be padded on its right side
        with as much blank characters as necessary to reach the required
        `width`. In contrast, if the string is wider than `width` then all
        characters on the right side of the string which are "too much" are
        truncated.
        """
        return '%%-%d.%ds' % (width, width)

    @staticmethod
    def get_unpadded_template(width):
        """
        Same as `get_padded_template()` but does not pad blank characters if
        the string passed to the template is shorter than the given `width`.
        """
        return '%%.%ds' % width


class MappingFormatter(SequenceFormatter):
    """
    A class to do columnized formatting on a given mapping of strings.
    """

    @staticmethod
    def get_sorted(mapping):
        return collections.OrderedDict(
            (key, mapping[key]) for key in helpers.get_sorted(mapping.keys())
        )

    def get_decoded(self, mapping):
        keys = helpers.get_decoded(mapping.keys(), self.encoding)
        values = helpers.get_decoded(mapping.values(), self.encoding)
        return collections.OrderedDict(zip(keys, values))

    def get_line_properties(self, mapping):
        items = itertools.chain.from_iterable(mapping.items())
        return self.calculator.get_line_properties(items)

    @staticmethod
    def make_line_chunks(mapping, props):
        return list(mapping.items())[:props.num_lines]


def build_formatter(items_type, calculator=None, sort_items=False):
    if issubclass(items_type, collections.Mapping):
        formatter_class = MappingFormatter
    else:
        formatter_class = SequenceFormatter
    if calculator is None:
        calculator = ColumnWidthCalculator()
    return formatter_class(calculator, sort_items=sort_items)
