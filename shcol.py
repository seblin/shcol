# Copyright (c) 2013, Sebastian Linke

# Released under the Simplified BSD license 
# (see LICENSE file for details).

from __future__ import print_function

import collections
import os

LineProperties = collections.namedtuple(
    'LineProperties', 'column_widths, spacing, num_lines'
)

def columnize(items, spacing=2, max_line_width=80):
    """
    Return a columnized string based on `items`. The result is similar to the
    output generated by tools like `ls`.

    `spacing` defines the number of blank characters between two columns. 

    `max_line_width` defines the maximum amount of characters per line.

    Note that users don't need to define particular column widths, since the
    underlying algorithm will find an "ideal" configuration on its own. When
    doing this, it guarantees to keep `items` in their original order.
    """
    column_width_calculator = ColumnWidthCalculator(spacing, max_line_width)
    return Formatter(column_width_calculator).format(items)


class ColumnWidthCalculator(object):
    """
    A class with capabilities to calculate the widths for an unknown number
    of columns based on a given list of strings.
    """
    def __init__(self, spacing=2, max_line_width=80):
        """
        Initialize the calculator. `spacing` defines the number of spaces 
        between two columns. `max_line_width` is the maximal amount of 
        characters that a line may consume.
        """
        self.spacing = spacing
        self.max_line_width = max_line_width

    def get_properties(self, items):
        """
        Return a namedtuple containing meaningful properties that may be used 
        to format `items` as a columnized string. The members of the tuple 
        are: `column_widths`, `spacing`, `num_lines`.
        """
        item_widths = [len(item) for item in items]
        if not item_widths:
            column_widths, num_lines = [], 0
        elif any(width >= self.max_line_width for width in item_widths):
            # use only one column for all items
            column_widths, num_lines = [self.max_line_width], len(item_widths)
        else:
            column_widths, num_lines = self.calculate_columns(item_widths)
        return LineProperties(column_widths, self.spacing, num_lines)

    def calculate_columns(self, item_widths):
        """
        Calculate column widths based on `item_widths`, expecting `item_widths` 
        to be a list of non-negative integers that represent the length of each 
        corresponding string. The result is returned as a tuple consisting of 
        two elements: A list of calculated column widths and the number of 
        lines needed to display all items when using that information to do 
        columnized formatting.

        Note that this instance's `.max_line_width` and `.spacing` attributes 
        are taken into account when calculation is done. However, the column
        widths of the resulting tuple will *not* include that spacing.

        The goal of this implementation is to find a configuration suitable 
        for formatting that consumes as few lines as possible. It does not
        care about balanced column heights. This strategy might result in a
        configuration where the last column would hold a significant lower 
        amount of items compared to the preceding ones. Subclasses are free
        to change that behavior by reimplementing this method.
        """
        num_items = len(item_widths)
        for num_lines in range(1, num_items + 1):
            column_widths = [
                max(item_widths[i : i + num_lines])
                for i in range(0, num_items, num_lines)
            ]
            if self.fits_in_line(column_widths):
                break
        return column_widths, num_lines

    def fits_in_line(self, column_widths):
        """
        Summarize the values of given `column_widths`, add `.spacing` between
        each column and then check whether it exceeds `.max_line_width`. Return
        `True` if the result does *not* exceed the allowed line width. Return
        `False` otherwise.
        """
        total = sum(column_widths) + (len(column_widths) - 1) * self.spacing
        return total <= self.max_line_width

class Formatter(object):
    """
    A class to do columnized formatting on a given list of strings.
    """
    def __init__(self, column_width_calculator=None,
                 allow_exceeding=True, linesep=os.linesep):
        """
        Initialize the formatter. 

        `column_width_calculator` will be used to determine the width of each 
        column when columnized string formatting is done. It should be a class 
        instance that implements a `.get_properties()` method in a similar way 
        as `ColumnWidthCalculator` does. An instance of that class (using its 
        default values) is automatically created if `None` is passed instead.

        `linesep` defines the character(s) used to start a new line.

        `allow_exceeding` should be a boolean value defining whether a line
        that contains *only one item* may exceed the column width returned by 
        the calculator. This is meant to be used when the calculator's maximal
        line width is the same as the terminal's line width (which should be
        the default case). An item would then allowed to be wrapped over two 
        (or more) lines by the terminal in cases where it is the only item in 
        that line *and* has a width wider than the terminal's line. 

        Note that lines containing more than one item are not affected by this 
        option. The formatter will then just truncate them at their end once 
        they exceed the allowed width.
        """
        if column_width_calculator is None:
            column_width_calculator = ColumnWidthCalculator()
        self.column_width_calculator = column_width_calculator
        self.allow_exceeding = allow_exceeding
        self.linesep = linesep

    def format(self, items):
        """
        Return a columnized string based on `items`. Lines are joined by using
        this instance's `.linesep` attribute.
        """
        lines = self.iter_lines(items)
        return self.linesep.join(lines)

    def iter_lines(self, items):
        """
        Return columnized lines for `items` yielded by an iterator. Lines will
        *not* contain any extra newline characters at their end.
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
                cached_template = get_template(column_widths, props.spacing)
                yield cached_template % line_items

    def get_line_template(self, column_widths, spacing=2):
        """
        Return a string meant to be used as a formatting template for *one* 
        line of columnized output. The template will be suitable for old-style
        string formatting ('%s' % my_string). 

        `column_widths` is expected to be a list of integers representing the 
        width of each column (with the idea in mind that the template will be
        re-used for many lines). This information is used to generate according 
        format specifiers. In the resulting template the specifiers are joined 
        by using a separator with a `spacing` number of space characters.

        If this instance's `.allow_exceeding` attribute is set to `True` (or
        to be more exact: something that evaluates to `True`) then the last 
        (right-most) specifier will always be `'%s'`. If `column_widths` is 
        empty then the resulting template will be just an empty string.

        Specifiers are generated in a form such that any string exceeding its
        column's width will be truncated when applied via string formatting. 
        This truncation will be made to the right end of the affected string.
        If a string is shorter than its column's width then the rest of the
        column will be filled with blank characters.
        """
        if not column_widths:
            return ''
        if len(column_widths) == 1 and self.allow_exceeding:
            return '%s'
        specs = ['%%-%d.%ds' % (width, width) for width in column_widths[:-1]]
        specs.append('%%.%ds' % column_widths[-1])
        return (spacing * ' ').join(specs)


def test(items=None, spacing=2, max_line_width=80, sort_items=True):
    if items is None:
        items = globals().keys()
    if sort_items:
        items = sorted(items, key=str.lower)
    print(columnize(items, spacing, max_line_width))
