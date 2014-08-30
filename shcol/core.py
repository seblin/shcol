# -*- coding: utf-8 -*
# Copyright (c) 2013-2014, Sebastian Linke

# Released under the Simplified BSD license 
# (see LICENSE file for details).

from __future__ import unicode_literals
import collections
import itertools

from . import config, helpers

__all__ = ['columnize']

LineProperties = collections.namedtuple(
    'LineProperties', 'column_widths, spacing, num_lines'
)

def columnize(
    items, spacing=config.SPACING, line_width=config.LINE_WIDTH,
    sort_items=config.SORT_ITEMS
):
    """
    Return a columnized string based on `items`. The result is similar to
    the output generated by tools like `ls`.

    `spacing` should be a positive integer defining the number of blank
    characters between two columns.

    `line_width` should be a positive integer defining the maximal amount
    of characters that fit in one line. If this is `None` then the terminal's
    width is used.

    If `sort_items` is `True`, then a locale-aware sorted version of `items`
    is used to generate the columnized output.

    Note that enabling `sort_items` may temporary change the interpreter's
    global locale configuration and thus is not thread-safe (which might be
    relevant in some cases). Leave this option disabled if you want to avoid
    this.
    """
    formatter = build_formatter(type(items), spacing, line_width, sort_items)
    return formatter.format(items)


class ColumnWidthCalculator(object):
    """
    A class with capabilities to calculate the widths for an unknown number
    of columns based on a given sequence of strings.
    """
    def __init__(
        self, spacing=config.SPACING, line_width=config.LINE_WIDTH,
        num_columns=None, allow_exceeding=True
    ):
        """
        Initialize the calculator.
        
        `spacing` defines the number of blanks between two columns.
        
        `line_width` is the maximal amount of characters that fits in one line.
        
        `num_columns` defines a fixed number of columns to be used for column
        width calculation. This can be `None` to let the calculator decide about
        the number of columns on its own. Note that the "`None`-mode" is often
        useful when the input is just something like a list of names where the
        resulting number of columns fitting in one line is usually unknown,
        while the "fixed-mode" make sense when you have structured input where
        the number of resulting columns is essential (e.g. in mappings).
        
        If `allow_exceeding` is set to `True` then the calculator is allowed to
        exceed the given line width in cases where `num_columns` is `None` *and*
        at least one item of the input is wider than the allowed line width. The
        result will then consist of only one column and that column's width will
        equal to the widest item's width. Note that in all other constellations
        a `ValueError` will be raised instead.
        """
        self.spacing = spacing
        self.line_width = line_width
        if self.line_width is None:
            try:
                self.line_width = helpers.get_terminal_width()
            except (IOError, OSError):
                self.line_width = config.LINE_WIDTH_FALLBACK
        self.num_columns = num_columns
        self.allow_exceeding = allow_exceeding

    def get_line_properties(self, items):
        """
        Return a namedtuple containing meaningful properties that may be used
        to format `items` as a columnized string.

        The members of the tuple are: `column_widths`, `spacing`, `num_lines`.
        """
        item_widths = [len(item) for item in items]
        column_widths, num_lines = self.calculate_columns(item_widths)
        return LineProperties(column_widths, self.spacing, num_lines)

    def calculate_columns(self, item_widths):
        """
        Calculate column widths based on `item_widths`, expecting `item_widths`
        to be a sequence of non-negative integers that represent the length of
        each corresponding string. The result is returned as a tuple consisting
        of two elements: A sequence of calculated column widths and the number
        of lines needed to display all items when using that information to do
        columnized formatting.

        Note that this instance's `.line_width` and `.spacing` attributes are
        taken into account when calculation is done. However, the column widths
        of the resulting tuple will *not* include that spacing.
        """
        if not item_widths:
            return [], 0
        if self.num_columns is None:
            max_columns = self.calculate_max_columns(item_widths)
            candidates = self.get_column_configs(item_widths, max_columns)
            for column_widths, num_lines in candidates:
                if self.fits_in_line(column_widths):
                    return column_widths, num_lines
            column_widths, num_lines = [max(item_widths)], len(item_widths)
        else:
            column_widths, num_lines = self.get_widths_and_lines(
                item_widths, self.num_columns
            )
        if not self.allow_exceeding and not self.fits_in_line(column_widths):
            raise ValueError('items do not fit in line')
        return column_widths, num_lines

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
        if widest_item >= self.line_width:
            return 1
        remaining_width = self.line_width - widest_item
        min_width = self.spacing + smallest_item
        possible_columns = 1 + remaining_width // min_width
        return min(num_items, possible_columns)

    def get_column_configs(self, item_widths, max_columns):
        """
        Return an iterator that yields all possible "column configurations" for
        `item_widths`. A configuration is a 2-element tuple consisting of a list
        of column widths and the number of lines that are needed to display all
        items with that configuration. The maximum number of columns is defined
        by `max_columns`.
        
        Note that `max_columns` is also used to define the initial amount of
        columns for the first configuration. Subsequent configurations are
        calculated by decreasing that amount by one at each step until an
        amount of zero columns is reached.
        """
        for num_columns in range(max_columns, 0, -1):
            yield self.get_widths_and_lines(item_widths, num_columns)

    @staticmethod
    def get_widths_and_lines(item_widths, num_columns):
        """
        Calulate column widths based on `item_widths` for an amount of
        `num_columns` per line. The resulting column widths are represented
        as a list of positive integers. This list and the number of lines
        needed to display all items is returned as a 2-element tuple.
        """
        num_items = len(item_widths)
        num_lines = num_items // num_columns + bool(num_items % num_columns)
        column_widths = [
            max(item_widths[i : i + num_lines])
            for i in range(0, num_items, num_lines)
        ]
        return column_widths, num_lines

    def fits_in_line(self, column_widths):
        """
        Summarize the values of given `column_widths`, add `.spacing` between
        each column and then check whether it exceeds `.line_width`. Return
        `True` if the result does *not* exceed the allowed line width. Return
        `False` otherwise.
        """
        total = sum(column_widths) + (len(column_widths) - 1) * self.spacing
        return total <= self.line_width


class IterableFormatter(object):
    """
    A class to do columnized formatting on a given iterable of strings.
    """
    def __init__(
        self, calculator, linesep=config.LINESEP, encoding=config.ENCODING,
        sort_items=config.SORT_ITEMS
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

        `sort_items` defines whether the given items should be sorted before
        they are columnized.
        """
        self.calculator = calculator
        self.linesep = linesep
        self.encoding = encoding
        self.sort_items = sort_items

    def format(self, items):
        """
        Return a columnized string based on `items`.
        """
        if self.sort_items:
            items = self.get_sorted(items)
        decoded_items = self.get_decoded(items)
        lines = self.make_lines(decoded_items)
        return self.linesep.join(lines)

    @staticmethod
    def get_sorted(items):
        """
        Return a sorted version of `items`.
        """
        return helpers.get_sorted(items)

    def get_decoded(self, items):
        """
        Return a version of `items` where each element is guaranteed to be a
        unicode-string. If `items` contains byte-strings then these strings
        are decoded to unicode by using the codec specified in the `encoding`-
        attribute of this instance. Items that are already unicode-strings are
        left unchanged. A `TypeError` is raised if `items` contains non-string
        elements.
        """
        return list(helpers.get_decoded(items, self.encoding))

    def make_lines(self, items):
        """
        Return columnized lines for `items` yielded by an iterator. Note that
        this method does not append extra newline characters to the end of the
        resulting lines.
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
        """
        Return a `LineProperties`-instance with a configuration based on given
        `items`.
        """
        return self.calculator.get_line_properties(items)

    @staticmethod
    def make_line_chunks(items, props):
        """
        Return an iterable of tuples that represent the elements of `items` for
        each line meant to be used in a formatted string. Note that the result
        depends on the value of `props.num_lines` where `props` should be a
        `LineProperties`-instance.
        """
        return [
            tuple(items[i::props.num_lines]) for i in range(props.num_lines)
        ]

    def make_line_template(self, props, num_columns=None):
        """
        Return a string meant to be used as a formatting template for *one* line
        of columnized output. The template will be suitable for old-style string
        formatting ('%s' % my_string). 

        `props` is expected to be a `LineProperties`-instance as it is defined
        in this module. Appropriated format specifiers are generated based on
        the information of `props.column_widths`. In the resulting template the
        specifiers are joined by using a separator with a `props.spacing` number
        of blank characters.

        `num_columns` defines the number of columns that the resulting template
        should cover. If `None` is used then all items of `props.columns_widths`
        are taken into account. Otherwise, the resulting format string will only
        hold specifiers for the first `num_columns`.
        """
        widths = props.column_widths[:num_columns]
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


class MappingFormatter(IterableFormatter):
    """
    A class to do columnized formatting on a given mapping of strings.
    """
    @staticmethod
    def get_sorted(mapping):
        """
        Return a sorted version of `mapping`.
        """
        return helpers.get_dict(
            (key, mapping[key]) for key in helpers.get_sorted(mapping.keys())
        )

    def get_decoded(self, mapping):
        """
        Return a version of `mapping` where each element is guaranteed to be a
        unicode-string. If `mapping` contains byte-strings then these strings
        are decoded to unicode by using the codec specified in the `encoding`-
        attribute of this instance. Items that are already unicode-strings are
        left unchanged. A `TypeError` is raised if `mapping` contains non-string
        elements.
        """
        keys = helpers.get_decoded(mapping.keys(), self.encoding)
        values = helpers.get_decoded(mapping.values(), self.encoding)
        return helpers.get_dict(zip(keys, values))

    def get_line_properties(self, mapping):
        """
        Return a `LineProperties`-instance with a configuration based on the
        strings in the keys and values of `mapping`.
        """
        items = itertools.chain(mapping.keys(), mapping.values())
        return self.calculator.get_line_properties(items)

    @staticmethod
    def make_line_chunks(mapping, props):
        """
        Return an iterable of tuples that represent the elements of `mapping`
        for each line meant to be used in a formatted string. Note that the
        result depends on the value of `props.num_lines` where `props` should
        be a `LineProperties`-instance.
        """
        return list(mapping.items())[:props.num_lines]


def build_formatter(
    items_type, spacing=config.SPACING, line_width=config.LINE_WIDTH,
    sort_items=config.SORT_ITEMS, calculator_class=ColumnWidthCalculator
):
    """
    Return a new formatter instance based on the given parameters.

    `items_type` defines the container type of the items that are meant to
    be formatted (list, dict, tuple, ...). In its current implementation only
    mapping types are special-cased by this function. All other types are just
    treated as iterables.

    `spacing` defines the number of blank characters between two columns.

    `line_width` is the maximal amount of characters that fits in one line.
    If this is set to `None` then the terminal's width is used. Note that
    setting a numeric value to this parameter guarantees that the given
    line width is never exceeded when rendered with columnized items. A
    `ValueError` is thrown in cases where this guarantee can't be fulfilled
    (e.g. at least one item is wider than the allowed line width). In
    contrast, setting that parameter to `None` will not give that guarantee.
    The underlying calculator is then free do decide whether throwing an
    exception is reasonable.

    `sort_items` defines whether items should be sorted.

    `calculator_class` defines the class to use for column width calculation.
    It should implement a `get_line_properties`-method and it should provide an
    `__init__`-method with the same signature as `ColumnWidthCalculator` does.
    """
    if issubclass(items_type, collections.Mapping):
        formatter_class = MappingFormatter
        calculator = calculator_class(
            spacing, line_width, num_columns=2, allow_exceeding=False
        )
    else:
        formatter_class = IterableFormatter
        calculator = calculator_class(
            spacing, line_width, allow_exceeding=(line_width is None)
        )
    return formatter_class(calculator, sort_items=sort_items)
