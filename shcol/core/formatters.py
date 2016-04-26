# -*- coding: utf-8 -*-
# Copyright (c) 2013-2015, Sebastian Linke

# Released under the Simplified BSD license
# (see LICENSE file for details).

import collections
import itertools

from .. import config, helpers
from . import columncalc

__all__ = ['get_formatter_class', 'IterableFormatter', 'MappingFormatter']

def get_formatter_class(items):
    """
    Return an appropriated class based on the type of `items`.

    If `items` is a dict-like object then `MappingFormatter` will be returned.
    Otherwise, `IterableFormatter` is returned.

    Note that these heuristics are based on rough assumptions. There is no
    guarantee that formatting with the returned class will not fail.
    """
    if isinstance(items, collections.Mapping):
        return MappingFormatter
    return IterableFormatter

class IterableFormatter(object):
    """
    A class to do columnized formatting on a given iterable of strings.
    """
    def __init__(
        self, calculator, linesep=config.LINESEP,
        encoding=config.ENCODING, autowrap=False
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
        return cls(columncalc.ColumnWidthCalculator(spacing, line_width))

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
        calculator = columncalc.ColumnWidthCalculator(
            spacing, width_info.window_width, allow_exceeding=True
        )
        return cls(calculator, autowrap=width_info.is_line_width)

    def format(self, items, pattern=None, sort_items=config.SORT_ITEMS):
        """
        Return a columnized string based on `items`.

        If `pattern` is not `None` then it is meant to be an expression that is
        free to make use of shell-like file matching mechanisms for matching a
        subset of `items` (e.g. "x*" to match all items starting with "x").

        `sort_items` should be a boolean defining whether `items` should be
        sorted before they are columnized.
        """
        if sort_items:
            items = self.get_sorted(items)
        items = self.get_strings(items)
        if pattern is not None:
            items = self.filter_names(items, pattern)
        lines = self.make_lines(items, add_line_breaks=True)
        return ''.join(lines).rstrip(self.linesep)

    def get_strings(self, items):
        """
        Return a Unicode version of `items`.
        """
        return helpers.get_strings(items, self.encoding)

    @staticmethod
    def filter_names(items, pattern):
        """
        Return a filtered version of `items` that only includes elements which
        match the given `pattern`.

        `pattern` is meant to be an expression that is free to make use of
        shell-like file matching mechanisms (e.g. "x*" to match all items
        starting with "x").
        """
        return helpers.filter_names(items, pattern)

    @staticmethod
    def get_sorted(items):
        """
        Return a sorted version of `items`.
        """
        return helpers.get_sorted(items)

    def make_lines(self, items, add_line_breaks=False):
        """
        Return columnized lines for `items` yielded by an iterator.

        If `add_line_breaks` is `True` then extra newline characters will be
        appended to the end of the resulting lines.
        """
        if isinstance(items, collections.Iterator):
            items = list(items)
        props = self.get_line_properties(items)
        line_chunks = self.make_line_chunks(items, props)
        lines = self.iter_formatted_lines(line_chunks, props)
        if add_line_breaks:
            lines = self.add_line_breaks(lines)
        return lines

    def add_line_breaks(self, lines):
        """
        Add line breaks to each line of given `lines`.

        If the `.autowrap`-attribute of this formatter is set to `True` then
        lines, which exactly match the formatter's line width, will *not* get
        a line break. This avoids an undesired empty line after those lines.
        """
        template = 'adding line breaks (linesep: {!r}, wrapsep: {!r})'
        config.LOGGER.debug(template.format(self.linesep, self.wrapsep))
        for lineno, line in enumerate(lines, 1):
            if len(line) == self.calculator.line_width:
                msg = 'adding wrapsep to line {}'.format(lineno)
                line += self.wrapsep
            else:
                msg = 'adding linesep to line {}'.format(lineno)
                line += self.linesep
            config.LOGGER.debug(msg)
            yield line

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
        min_shrink_width=10
    ):
        """
        Return a new instance of this class with a pre-configured calculator.
        The calculator instance will be based on the given `spacing` and
        `line_width` parameters.

        Use `min_shrink_width` to define the minimal width that a column may be
        shrinked to. Defining this as `None` means that columns are not allowed
        to be shrinked.
        """
        calculator = columncalc.ColumnWidthCalculator(
            spacing, line_width, num_columns=2,
            min_shrink_width=min_shrink_width
        )
        return cls(calculator)

    @classmethod
    def for_terminal(
        cls, terminal_stream=config.TERMINAL_STREAM, spacing=config.SPACING,
        min_shrink_width=10
    ):
        """
        Return a new instance of this class with a pre-configured calculator.
        The calculator instance will be based on given `spacing` and on the
        line width of `terminal_stream`.

        Note that this method will throw an `IOError` or `OSError` if getting
        the line width from `terminal_stream` failed.

        Use `min_shrink_width` to define the minimal width that a column may be
        shrinked to. Defining this as `None` means that columns are not allowed
        to be shrinked.
        """
        width_info = helpers.get_terminal_width_info(terminal_stream)
        calculator = columncalc.ColumnWidthCalculator(
            spacing, width_info.window_width, num_columns=2,
            min_shrink_width=min_shrink_width
        )
        return cls(calculator, autowrap=width_info.is_line_width)

    def get_strings(self, mapping):
        """
        Return a Unicode version of `mapping`.
        """
        keys = helpers.get_strings(mapping.keys(), self.encoding)
        values = helpers.get_strings(mapping.values(), self.encoding)
        return collections.OrderedDict(zip(keys, values))

    @staticmethod
    def filter_names(mapping, pattern):
        """
        Return a filtered version of `mapping` that only includes items whose
        keys match the given `pattern`.

        `pattern` is meant to be an expression that is free to make use of
        shell-like file matching mechanisms (e.g. "x*" to match all keys
        starting with "x").
        """
        return collections.OrderedDict(
            (k, mapping[k]) for k in helpers.filter_names(mapping, pattern)
        )

    @staticmethod
    def get_sorted(mapping):
        """
        Return a sorted version of `mapping`.
        """
        return collections.OrderedDict(
            (key, mapping[key]) for key in helpers.get_sorted(mapping)
        )

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
