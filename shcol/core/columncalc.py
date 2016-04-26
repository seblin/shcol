# -*- coding: utf-8 -*-
# Copyright (c) 2013-2016, Sebastian Linke

# Released under the Simplified BSD license
# (see LICENSE file for details).

import collections

from .. import config, helpers

class LineTooSmallError(Exception):
    """
    Meant to be raised when a line is too small to include all items.
    """
    def __init__(self, msg='items do not fit in line'):
        """
        `msg` is used for the error message when this exception is thrown.
        """
        self.msg = msg

    def __str__(self):
        return self.msg

LineProperties = collections.namedtuple(
    'LineProperties', 'column_widths, spacing, num_lines'
)

ColumnConfig = collections.namedtuple(
    'ColumnConfig', 'column_widths, num_lines'
)

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
                return ColumnConfig([self.line_width], len(item_widths))
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
                raise LineTooSmallError
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
            raise LineTooSmallError

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
            raise LineTooSmallError

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
