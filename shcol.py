# Copyright (c) 2013, Sebastian Linke

# Released under the Simplified BSD license 
# (see LICENSE file for details).

from __future__ import print_function

from collections import namedtuple
from itertools import count
import os

try:
    _range = xrange
except NameError:
    _range = range

LineProperties = namedtuple(
                   'LineProperties', 'column_widths, spacing, num_lines')

def columnize(items, spacing=2, max_line_width=80):
    """
    Return a string containing `items` placed in columns. The number of 
    whitespace characters between two columns is defined by `spacing`. 
    `max_line_width` defines the maximal amount of characters that may be 
    consumed per line (e.g. the current width of the terminal window).
    """
    column_width_calculator = ColumnWidthCalculator(spacing, max_line_width)
    return Formatter(column_width_calculator).format(items)


class ColumnWidthCalculator(object):
    """
    A class to calculate the width of each column for a given list of items.
    """
    def __init__(self, spacing=2, max_line_width=80):
        """
        Initialize the calculator. `spacing` defines the number of whitespace
        characters between two columns. `max_line_width` is the maximal amount
        of characters that a line may consume.
        """
        self.spacing = spacing
        self.max_line_width = max_line_width

    def get_properties(self, items):
        """
        Return a namedtuple containing suitable properties that may be used to 
        format `items` as a columnized string. The members of the tuple are:
        `column_widths`, `spacing`, `num_lines`.
        """
        self._check_values()
        item_widths = [len(item) for item in items]
        if not item_widths:
            column_widths, num_lines = [], 0
        elif any(width >= self.max_line_width for width in item_widths):
            column_widths, num_lines = [self.max_line_width], len(item_widths)
        else:
            column_widths, num_lines = self.calculate_columns(item_widths)
        return LineProperties(column_widths, self.spacing, num_lines)

    def _check_values(self):
        for value in (self.spacing, self.max_line_width):
            if not isinstance(value, int) or value < 0:
                msg = 'spacing and max_line_width must be non-negative integers'
                raise ValueError(msg)

    def calculate_columns(self, item_widths):
        """
        Calculate column widths based on `item_widths`, where `item_widths` is
        expected to be a list (or speaking more general: a container) whose
        elements represent the length of each corresponding string. The result 
        is returned as a tuple consisting of two elements: A list of calculated
        column widths and the number of lines needed to display all items when
        using that information to do columnized formatting. 

        Note that calculation takes respect to the `spacing` attribute of this
        method's instance. Though, a particular column width information does 
        *not* include spacing.

        The goal of this implementation is to find a configuration suitable for 
        formatting that consumes as few lines as possible. This may mean that 
        the resulting last column might hold a significant lower amount of 
        items compared to the preceding ones. Subclasses reimplementing this 
        method may apply a different strategy for that calculation.
        """
        num_items = len(item_widths)
        for line_size in count(1):
            column_widths = []
            line_width = -self.spacing
            for i in _range(0, num_items, line_size):
                column_width = max(item_widths[i : i + line_size])
                line_width += column_width + self.spacing
                if line_width > self.max_line_width:
                    # abort as early as possible and jump to next iteration 
                    # of outer loop (improves performance which is especially 
                    # notable when dealing with large amount of items)
                    break
                column_widths.append(column_width)
            else:
                # current line size made all items pass without exceedance 
                # of `.max_line_width` -> return result as we are done here
                return column_widths, line_size


class Formatter(object):
    def __init__(self, column_width_calculator=None,
                 allow_exceeding=True, linesep=os.linesep):
        if column_width_calculator is None:
            column_width_calculator = ColumnWidthCalculator()
        self.column_width_calculator = column_width_calculator
        self.allow_exceeding = allow_exceeding
        self.linesep = linesep

    def format(self, items):
        line_strings = self.iter_line_strings(items)
        return self.linesep.join(line_strings)

    def iter_line_strings(self, items):
        props = self.column_width_calculator.get_properties(items)
        template = self.get_line_template(props.column_widths, props.spacing)
        for i in _range(props.num_lines):
            line_items = tuple(items[i::props.num_lines])
            try:
                yield template % line_items
            except TypeError:
                # number of specs != len(line_items)
                # -> re-generate template
                column_widths = props.column_widths[:len(line_items)]
                template = self.get_line_template(column_widths, props.spacing)
                yield template % line_items

    def get_line_template(self, column_widths, spacing=2):
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
