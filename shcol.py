# Copyright (c) 2013, Sebastian Linke

# Released under the Simplified BSD license 
# (see LICENSE file for details).

import collections
import functools
import locale
import os

__all__ = ['columnize', 'ColumnWidthCalculator', 'Formatter', 'LineProperties']

LineProperties = collections.namedtuple(
    'LineProperties', 'column_widths, spacing, num_lines'
)

def columnize(items, spacing=2, max_line_width=80, sort_items=False):
    """
    Return a columnized string based on `items`. The result is
    similar to the  output generated by tools like `ls`.

    `spacing` defines the number of blank characters between
    two columns.

    `max_line_width` defines the maximum amount of characters
    per line.

    If `sort_items` is `True`, then a locale-aware sorted version
    of `items` is used to generate the columnized output.

    Note that enabling `sort_items` may temporary change the
    interpreter's global locale configuration and thus is not
    thread-safe (which might be relevant in some cases). Leave
    this option disabled (the default) if you want to avoid this.
    """
    if sort_items:
        sortkey = functools.cmp_to_key(locale.strcoll)
        with _DefaultLocale(locale.LC_COLLATE):
            items = sorted(items, key=sortkey)
    column_width_calculator = ColumnWidthCalculator(spacing, max_line_width)
    return Formatter(column_width_calculator).format(items)


class _DefaultLocale(object):
    def __init__(self, category):
        self.category = category
        self.old_locale = locale.getlocale(category)
        self.default_locale = locale.getdefaultlocale()

    def __enter__(self):
        locale.setlocale(self.category, self.default_locale)

    def __exit__(self, *unused):
        locale.setlocale(self.category, self.old_locale)


class ColumnWidthCalculator(object):
    """
    A class with capabilities to calculate the widths for an
    unknown number of columns based on a given list of strings.
    """
    def __init__(self, spacing=2, max_line_width=80):
        """
        Initialize the calculator. `spacing` defines the number
        of blanks between two columns. `max_line_width` is the
        maximal amount of characters that a line may consume.
        """
        self.spacing = spacing
        self.max_line_width = max_line_width

    def get_properties(self, items):
        """
        Return a namedtuple containing meaningful properties that
        may be used to format `items` as a columnized string.

        The members of the tuple are:

        `column_widths`, `spacing`, `num_lines`.
        """
        item_widths = [len(item) for item in items]
        column_widths, num_lines = self.calculate_columns(item_widths)
        return LineProperties(column_widths, self.spacing, num_lines)

    def calculate_columns(self, item_widths):
        """
        Calculate column widths based on `item_widths`, expecting
        `item_widths` to be a list of non-negative integers that
        represent the length of each corresponding string. The
        result is returned as a tuple consisting of two elements:
        A list of calculated column widths and the number of lines
        needed to display all items when using that information to
        do columnized formatting.

        Note that this instance's `.max_line_width` and `.spacing`
        attributes are taken into account when calculation is done.
        However, the column widths of the resulting tuple will *not*
        include that spacing.
        """
        max_columns = self.calculate_max_columns(item_widths)
        if max_columns == 0:
            return [], 0
        num_items = len(item_widths)
        for num_columns in range(max_columns, 0, -1):
            num_lines, remaining = divmod(num_items, num_columns)
            if remaining:
                num_lines += 1
            column_widths = [
                max(item_widths[i : i + num_lines])
                for i in range(0, num_items, num_lines)
            ]
            if self.fits_in_line(column_widths):
                return column_widths, num_lines
        return [self.max_line_width], len(item_widths)

    def calculate_max_columns(self, item_widths):
        """
        Return the number of columns that is guaranteed not
        to be exceeded when `item_widths` are columnized.

        This is meant to be used as an initial value on which
        the real calculation of resulting column widths may
        be based on. Using this value can save a remarkable
        number of iterations depending on the how the column
        width calculation is implemented.
        """
        if not item_widths:
            return 0
        smallest_item, widest_item = min(item_widths), max(item_widths)
        if widest_item >= self.max_line_width:
            return 1
        remaining_width = self.max_line_width - widest_item
        min_width = smallest_item + self.spacing
        possible_columns = 1 + remaining_width // min_width
        return min(len(item_widths), possible_columns)

    def fits_in_line(self, column_widths):
        """
        Summarize the values of given `column_widths`, add
        `.spacing` between each column and then check whether
        it exceeds `.max_line_width`. Return `True` if the
        result does *not* exceed the allowed line width. Return
        `False` otherwise.
        """
        total = sum(column_widths) + (len(column_widths) - 1) * self.spacing
        return total <= self.max_line_width

class Formatter(object):
    """
    A class to do columnized formatting on a given list of strings.
    """
    def __init__(
        self, column_width_calculator=None,
        allow_exceeding=True, linesep=os.linesep
    ):
        """
        Initialize the formatter. 

        `column_width_calculator` will be used to determine the
        width of each column when columnized string formatting
        is done. It should be a class instance that implements
        a `.get_properties()` method in a similar way as
        `ColumnWidthCalculator` does. An instance of that class
        (using its default values) is automatically created if
        `None` is passed instead.

        `linesep` defines the character(s) used to start a
        new line.

        `allow_exceeding` should be a boolean value defining
        whether a line that contains *only one item* may exceed
        the column width returned by the calculator. This is
        meant to be used when the calculator's maximal line
        width is the same as the terminal's line width (which
        should be the default case). An item would then allowed
        to be wrapped over two (or more) lines by the terminal
        in cases where it is the only item in that line *and*
        has a width wider than the terminal's line. 

        Note that lines containing more than one item are not
        affected by this option. The formatter will then just
        truncate them at their end once they exceed the allowed
        width.
        """
        if column_width_calculator is None:
            column_width_calculator = ColumnWidthCalculator()
        self.column_width_calculator = column_width_calculator
        self.allow_exceeding = allow_exceeding
        self.linesep = linesep

    def format(self, items, encoding='utf-8'):
        """
        Return a columnized string based on `items`. Note that
        any item that is a byte string will be converted to
        unicode using the codec name specified by `encoding`.
        """
        items = [self._decode(item, encoding) for item in items]
        return self.linesep.join(self.iter_lines(items))

    @staticmethod
    def _decode(item, encoding):
        return item.decode(encoding) if isinstance(item, bytes) else item

    def iter_lines(self, items):
        """
        Return columnized lines for `items` yielded by an
        iterator. Lines will *not* contain any extra newline
        characters at their end.
        """
        props = self.column_width_calculator.get_properties(items)
        get_template = self.get_line_template  # short alias
        template = get_template(props.column_widths, props.spacing)
        for i in range(props.num_lines):
            line_items = tuple(items[i::props.num_lines])
            try:
                yield template % line_items
            except TypeError:
                # number of specs != len(line_items)
                # -> re-generate template
                column_widths = props.column_widths[:len(line_items)]
                template = get_template(column_widths, props.spacing)
                yield template % line_items

    def get_line_template(self, column_widths, spacing=2):
        """
        Return a string meant to be used as a formatting
        template for *one* line of columnized output. The
        template will be suitable for old-style string
        formatting ('%s' % my_string). 

        `column_widths` is expected to be a list of integers
        representing the width of each column (with the idea
        in mind that the template will be re-used for many
        lines). This information is used to generate according 
        format specifiers. In the resulting template the
        specifiers are joined by using a separator with a
        `spacing` number of blank characters.

        Specifiers are generated in a form such that any
        string exceeding its column's width will be truncated
        when applied via string formatting. This truncation
        will be made to the right end of the affected string.
        If a string is shorter than its column's width then
        the rest of the column in that line will be filled
        with blank characters.
        """
        if not column_widths:
            return ''
        if len(column_widths) == 1 and self.allow_exceeding:
            return '%s'
        specs = ['%%-%d.%ds' % (width, width) for width in column_widths[:-1]]
        specs.append('%%.%ds' % column_widths[-1])
        return (spacing * ' ').join(specs)
