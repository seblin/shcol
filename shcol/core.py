# -*- coding: utf-8 -*-
# Copyright (c) 2013-2015, Sebastian Linke

# Released under the Simplified BSD license
# (see LICENSE file for details).

"""
Classes and functions providing the core functionality of `shcol`.
"""

from __future__ import unicode_literals
import collections
import itertools

from . import config, helpers

__all__ = ['columnize']


class LineTooSmallError(Exception):
    pass

LineProperties = collections.namedtuple(
    'LineProperties', 'column_widths, spacing, num_lines'
)

ColumnConfig = collections.namedtuple(
    'ColumnConfig', 'column_widths, num_lines'
)

def columnize(
    items, spacing=config.SPACING, line_width=config.LINE_WIDTH,
    make_unique=config.MAKE_UNIQUE, sort_items=config.SORT_ITEMS,
    decode=config.NEEDS_DECODING, output_stream=config.TERMINAL_STREAM
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

    If `make_unique` is `True` then only the first occurrence of an item is
    processed and any other occurrences of that item are ignored.

    If `sort_items` is `True`, then a locale-aware sorted version of `items`
    is used to generate the columnized output. Note that enabling sorting is not
    thread-safe because it temporarily changes the interpreter's global `locale`
    configuration.

    `decode` defines whether non-Unicode items should be decoded to Unicode. If
     running on Python 3.x then most of the time the "decoding step" is not
     necessary and can be skipped to safe some time. This is why the default
     value for `decode` is `False` when running on a Python 3.x interpreter
     while it is set to `True` when running on Python 2.x.

     `output_stream` defines the stream where the result should be written to.
    """
    if make_unique and not helpers.is_mapping(items):
        items = helpers.make_unique(items)
    formatter_class = get_formatter_class(items)
    if line_width is None:
        try:
            formatter = formatter_class.for_terminal(output_stream, spacing)
        except (IOError, OSError):
            raise ValueError('unable to detect line width')
    else:
        formatter = formatter_class.for_line_config(spacing, line_width)
    return formatter.format(items, sort_items, decode)

def get_formatter_class(items):
    """
    Return an appropriated class based on the type of `items`.

    If `items` is a dict-like object then `MappingFormatter` will be returned.
    Otherwise, `IterableFormatter` is returned.

    Note that these heuristics are based on rough assumptions. There is no
    guarantee that formatting with the returned class will not fail.
    """
    if helpers.is_mapping(items):
        return MappingFormatter
    return IterableFormatter


class IterableFormatter(object):
    """
    A class to do columnized formatting on a given iterable of strings.
    """
    def __init__(
        self, calculator, linesep=config.LINESEP, encoding=config.ENCODING,
        autowrap=False
    ):
        """
        Initialize the formatter.

        `calculator` will be used to determine the width of each column when
        columnized string formatting is done. It should be a class instance
        that implements a `.get_properties()` method in a similar way as
        `ColumnWidthCalculator` does.

        `linesep` defines the character(s) used to start a new line.

        `encoding` should be a string defining the codec name to be used in
        cases where decoding of items is requested.

        `autowrap` defines whether the resulting lines are wrapped automatically
        when exceeding the line width. If this is `True` then the formatter will
        *not* add newline characters to the "linebreaking" parts of these lines.
        """
        self.calculator = calculator
        self.linesep = linesep
        self.encoding = encoding
        self.wrapsep = '' if autowrap else linesep

    def __repr__(self):
        attrs = ['calculator', 'linesep', 'encoding', 'wrapsep']
        return helpers.make_object_repr(self, attrs)

    @classmethod
    def for_line_config(
        cls, spacing=config.SPACING, line_width=config.LINE_WIDTH
    ):
        """
        Return a new instance of this class with a pre-configured calculator.
        The calculator instance will be based on the given `spacing` and
        `line_width` parameters.
        """
        return cls(ColumnWidthCalculator(spacing, line_width))

    @classmethod
    def for_terminal(
        cls, terminal_stream=config.TERMINAL_STREAM, spacing=config.SPACING
    ):
        """
        Return a new instance of this class with a pre-configured calculator.
        The calculator instance will be based on given `spacing` and on the
        line width of `terminal_stream`.

        Note that this method will throw an `IOError` or `OSError` if getting
        the line width from `terminal_stream` failed.
        """
        width_info = helpers.get_terminal_width_info(terminal_stream)
        calculator = ColumnWidthCalculator(
            spacing, width_info.window_width, allow_exceeding=True
        )
        return cls(calculator, autowrap=width_info.is_line_width)

    def format(
        self, items, sort_items=config.SORT_ITEMS, decode=config.NEEDS_DECODING
    ):
        """
        Return a columnized string based on `items`.

        `sort_items` should be a boolean defining whether `items` should be
        sorted before they are columnized.

        `decode` defines whether each item should be decoded in order to get
        Unicode-strings. When passing items that already are Unicode then this
        parameter may be set to `False` to skip the "decoding step" (which will
        safe some time).

        Please note that Python 2.x (byte-)strings with non-ascii characters in
        it (e.g. German umlauts) should always be decoded. Otherwise, formatting
        is likely to return unexpected results. Unicode items in Python 2.x are
        *not* affected by this.
        """
        if sort_items:
            items = self.get_sorted(items)
        if decode:
            items = self.get_decoded(items)
        lines = self.make_lines(items)
        return self.linesep.join(lines)

    @staticmethod
    def get_sorted(items):
        """
        Return a sorted version of `items`.
        """
        return helpers.get_sorted(items)

    def get_decoded(self, items):
        """
        Return a decoded version of `items`.
        """
        return helpers.get_decoded(items, self.encoding)

    def make_lines(self, items):
        """
        Return columnized lines for `items` yielded by an iterator. Note that
        this method does not append extra newline characters to the end of the
        resulting lines.
        """
        if isinstance(items, collections.Iterator):
            items = list(items)
        props = self.get_line_properties(items)
        line_chunks = self.make_line_chunks(items, props)
        return self.iter_formatted_lines(line_chunks, props)

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

    def iter_formatted_lines(self, line_chunks, props):
        """
        Return formatted lines as an iterator.

        `line_chunks` should be an iterable providing chunks of line items. In
        other words: Each chunk yielded by the iterable should represent the
        items to be used for one line of output.

        `props` is expected to be a `LineProperties`-instance. It is used to
        define the exact formatting of the resulting lines.

        Note that this method is able to detect items that are wider than the
        corresponding column width of `props`. Exceeding parts of these items
        are arranged over multiple lines when displayed in a terminal. They are
        guaranteed to always appear in the "right" column.
        """
        template = self.make_line_template(props)
        for chunk in line_chunks:
            line = []
            num_wraps = max(
                len(item) // width - int(len(item) % width == 0)
                for item, width in zip(chunk, props.column_widths)
            )
            for i in range(num_wraps + 1):
                wrapped_chunk = tuple(
                    item[pos * i : pos * (i + 1)] for item, pos
                    in zip(chunk, props.column_widths)
                )
                try:
                    line.append(template % wrapped_chunk)
                except TypeError:
                    # cached template does not match current chunk length
                    # -> regenerate and try again
                    template = (
                        self.make_line_template(props, len(wrapped_chunk))
                    )
                    line.append(template % wrapped_chunk)
            yield self.wrapsep.join(line)

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
    @classmethod
    def for_line_config(
        cls, spacing=config.SPACING, line_width=config.LINE_WIDTH,
        min_shrink_width=5
    ):
        """
        Return a new instance of this class with a pre-configured calculator.
        The calculator instance will be based on the given `spacing` and
        `line_width` parameters.
        """
        calculator = ColumnWidthCalculator(
            spacing, line_width, num_columns=2,
            min_shrink_width=min_shrink_width
        )
        return cls(calculator)

    @classmethod
    def for_terminal(
        cls, terminal_stream=config.TERMINAL_STREAM, spacing=config.SPACING,
        min_shrink_width=5
    ):
        """
        Return a new instance of this class with a pre-configured calculator.
        The calculator instance will be based on given `spacing` and on the
        line width of `terminal_stream`.

        Note that this method will throw an `IOError` or `OSError` if getting
        the line width from `terminal_stream` failed.
        """
        width_info = helpers.get_terminal_width_info(terminal_stream)
        calculator = ColumnWidthCalculator(
            spacing, width_info.window_width, num_columns=2,
            min_shrink_width=min_shrink_width
        )
        return cls(calculator, autowrap=width_info.is_line_width)

    @staticmethod
    def get_sorted(mapping):
        """
        Return a sorted version of `mapping`.
        """
        return collections.OrderedDict(
            (key, mapping[key]) for key in helpers.get_sorted(mapping.keys())
        )

    def get_decoded(self, mapping):
        """
        Return a decoded version of `mapping`.
        """
        keys = helpers.get_decoded(mapping.keys(), self.encoding)
        values = helpers.get_decoded(mapping.values(), self.encoding)
        return collections.OrderedDict(zip(keys, values))

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


class ColumnWidthCalculator(object):
    """
    A class with capabilities to calculate the widths for an unknown number
    of columns based on a given sequence of strings.
    """
    def __init__(
        self, spacing=config.SPACING, line_width=config.LINE_WIDTH,
        num_columns=None, allow_exceeding=False, min_shrink_width=None
    ):
        """
        Initialize the calculator.
        
        `spacing` defines the number of blanks between two columns.
        
        `line_width` is the maximal amount of characters that fit in one line.

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

        Use `min_shrink_width` to define the minimal width that a column may be
        shrinked to. Defining this as `None` means that columns are not allowed
        to be shrinked.
        """
        self.spacing = helpers.num(spacing, allow_zero=True)
        self.line_width = helpers.num(line_width)
        self.num_columns = helpers.num(num_columns, allow_none=True)
        self.allow_exceeding = allow_exceeding
        self.min_shrink_width = helpers.num(min_shrink_width, allow_none=True)

    def __repr__(self):
        attrs = [
            'spacing', 'line_width', 'num_columns', 'allow_exceeding',
            'min_shrink_width'
        ]
        return helpers.make_object_repr(self, attrs)

    @staticmethod
    def raise_line_too_small_error(msg='items do not fit in line'):
        """
        Raise an error saying that the allowed line width is too small.

        Use `msg` to define the error message.
        """
        raise LineTooSmallError(msg)

    def get_line_properties(self, items):
        """
        Return a namedtuple containing meaningful properties that may be used
        to format `items` as a columnized string.

        The members of the tuple are: `column_widths`, `spacing`, `num_lines`.
        """
        item_widths = [len(item) for item in items]
        cfg = self.calculate_columns(item_widths)
        return LineProperties(cfg.column_widths, self.spacing, cfg.num_lines)

    def calculate_columns(self, item_widths):
        """
        Calculate column widths based on `item_widths`, expecting `item_widths`
        to be a sequence of non-negative integers that represent the length of
        each corresponding string. The result is returned as a named tuple that
        consists of two elements: A sequence of calculated column widths and the
        number of lines needed to display all items when using that information
        to do columnized formatting.

        Note that this instance's `.line_width` and `.spacing` attributes are
        taken into account when calculation is done. However, the column widths
        of the resulting tuple will *not* include that spacing.
        """
        if not item_widths:
            return ColumnConfig([], 0)
        try:
            return self.get_column_config(item_widths)
        except LineTooSmallError:
            if self.allow_exceeding and self.num_columns in (None, 1):
                return ColumnConfig([max(item_widths)], len(item_widths))
            else:
                raise

    def get_column_config(self, item_widths):
        """
        Return a column configuration based on `item_widths`.

        Note that the number of columns to use is retrieved from this instance's
        `.num_columns`-attribute. If the attribute was set to `None` then the
        algorithm will automatically determine a reasonable number of columns.
        """
        if self.num_columns is None:
            return self.find_fitting_config(item_widths)
        cfg = self.get_unchecked_column_config(item_widths, self.num_columns)
        if not self.fits_in_line(cfg.column_widths):
            if self.min_shrink_width is None:
                self.raise_line_too_small_error()
            column_widths = self.shrink_column_widths(cfg.column_widths)
            return ColumnConfig(column_widths, cfg.num_lines)
        return cfg

    def find_fitting_config(self, item_widths):
        """
        Return a column configuration that fits with the maximal line width of
        this instance.

        Note that this method internally uses `.iter_column_configs()` in order
        to retrieve some candidates and then returns the first fitting one. If
        no fitting candidate was found then this method will fail with an error.
        """
        max_columns = self.calculate_max_columns(item_widths)
        for cfg in self.iter_column_configs(item_widths, max_columns):
            if self.fits_in_line(cfg.column_widths):
                return cfg
        else:
            self.raise_line_too_small_error()

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

    def iter_column_configs(self, item_widths, max_columns):
        """
        Return an iterator that yields a sequence of "column configurations" for
        `item_widths`. A configuration is a 2-element tuple consisting of a list
        of column widths and the number of lines that are needed to display all
        items with that configuration. The maximum number of columns is defined
        by `max_columns`.
        
        Note that `max_columns` is also used to define the initial amount of
        columns for the first configuration. Subsequent configurations are
        calculated by decreasing that amount at each step until an amount of
        zero columns is reached.

        Depending on the underlying algorithm this method must not necessarily
        return each possible configuration. In fact, the current implementation
        prefers balanced column lengths where only the last column is allowed to
        be shorter than the other columns. This might result in omitting some
        configurations. See `.get_unchecked_column_config()` for details.
        """
        while max_columns > 0:
            cfg = self.get_unchecked_column_config(item_widths, max_columns)
            max_columns = len(cfg.column_widths) - 1
            yield cfg

    @staticmethod
    def get_unchecked_column_config(item_widths, max_columns):
        """
        Calculate column widths based on `item_widths` for an amount of at most
        `max_columns` per line. The resulting column widths are represented
        as a list of non-negative integers. This list and the number of lines
        needed to display all items is returned as a 2-element tuple.

        Note that this method does *not* check whether the resulting column
        width configuration would fit in a line. Also it does *not* take any
        spacing into account.

        This algorithm prefers balanced column lengths over matching exactly
        `max_columns`. Only the last column is allowed to be shorter than the
        other columns. This means that you might encounter results which have a
        much fewer number of columns than you had requested. In consequence of
        this, two requests with different `max_columns` might return the same
        result.
        """
        num_items = len(item_widths)
        max_columns = helpers.num(max_columns)
        num_lines, remaining = divmod(num_items, max_columns)
        if remaining:
            num_lines += 1
        column_widths = [
            max(item_widths[i : i + num_lines])
            for i in range(0, num_items, num_lines)
        ]
        return ColumnConfig(column_widths, num_lines)

    def shrink_column_widths(self, column_widths):
        """
        Return a shrinked version of `column_widths` so that the result will fit
        with this instance's allowed line width.

        Note that shrinking is done from the rightmost column to the leftmost
        column. The algorithm does not shrink more than necessary.

        Example: Allowed line width is 80, columns are [48, 35] and spacing=2.
        => 85 total width (including spacing)
        => columns after shrinking [48, 30].
        """
        offset = self.get_used_line_width(column_widths) - self.line_width
        processed = []
        for width in reversed(column_widths):
            if offset <= 0:
                # All widths fit in line
                break
            if width <= self.min_shrink_width:
                # This width was small from the beginning
                # => don't touch it!
                processed.append(width)
            else:
                new_width = width - offset
                if new_width < self.min_shrink_width:
                    new_width = self.min_shrink_width
                offset -= width - new_width
                processed.append(new_width)
        if offset > 0:
            self.raise_line_too_small_error()

        # Now merge untouched widths with processed widths
        if not processed:
            return column_widths
        result = column_widths[:-len(processed)]
        result.extend(reversed(processed))
        return result

    def fits_in_line(self, column_widths):
        """
        Return whether columnizing based on `column_widths` would fit with the
        allowed line width of this instance.
        """
        return self.get_used_line_width(column_widths) <= self.line_width

    def get_used_line_width(self, column_widths):
        """
        Return the line width that would be used if columnizing was based on
        given `column_widths`.
        """
        return sum(column_widths) + (len(column_widths) - 1) * self.spacing
