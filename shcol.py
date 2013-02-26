from __future__ import division, print_function

from collections import namedtuple
from itertools import count
from math import ceil

try:
    _range = xrange
except NameError:
    _range = range

LineProperties = namedtuple('LineProperties', 'column_widths, spacing')

def columnize(items, spacing=2, max_line_width=80):
    line_properties = LinePropertyBuilder(
                        items, spacing, max_line_width).get_properties()
    formatter = Formatter(line_properties, items)
    return '\n'.join(formatter.line_strings)

class LinePropertyBuilder(object):
    def __init__(self, items, spacing, max_line_width):
        self.item_widths = [len(item) for item in items]
        self.spacing = spacing
        self.max_line_width = max_line_width

    def get_properties(self):
        return LineProperties(self.get_column_widths(), self.spacing)

    def get_column_widths(self):
        self._check_values()
        if not self.item_widths:
            return []
        if any(width > self.max_line_width for width in self.item_widths):
            return [self.max_line_width]
        return self._calculate_column_widths()

    def _check_values(self):
        for value in (self.spacing, self.max_line_width):
            if not isinstance(value, int) or value < 0:
                msg = 'spacing and max_line_width must be non-negative integers'
                raise ValueError(msg)

    def _calculate_column_widths(self):
        num_items = len(self.item_widths)
        for chunk_size in count(1):
            column_widths = []
            line_width = -self.spacing
            for i in _range(0, num_items, chunk_size):
                column_width = max(self.item_widths[i : i + chunk_size])
                line_width += column_width + self.spacing
                if line_width > self.max_line_width:
                    break
                column_widths.append(column_width)
            else:
                return column_widths


class Formatter(object):
    def __init__(self, line_properties, items=[]):
        self.line_properties = line_properties
        self.items = items

    @property
    def line_strings(self):
        num_columns = self.num_columns
        if num_columns == 0:
            yield ''
            return
        num_lines = int(ceil(len(self.items) / num_columns))
        template = self.get_line_template()
        for i in _range(num_lines):
            line_items = tuple(self.items[i::num_lines])
            try:
                yield template % line_items
            except TypeError:
                # raised if last line contains too few items for line template
                # -> re-generate template for real number of items
                template = self.get_line_template(len(line_items))
                yield template % line_items

    @property
    def num_columns(self):
        return len(self.line_properties.column_widths)

    def get_line_template(self, num_specs=-1, allow_exceeding=True):
        if num_specs > self.num_columns:
            msg = 'not enough column widths to fill requested number of specs'
            raise ValueError(msg)
        if num_specs < 0:
            num_specs = self.num_columns
        if num_specs == 0:
            return ''
        if num_specs == 1 and allow_exceeding:
            return '%s'
        column_widths = self.line_properties.column_widths
        specs = ['%%-%d.%ds' % (width, width)
                 for width in column_widths[:num_specs - 1]]
        specs.append('%%.%ds' % column_widths[num_specs - 1])
        return (self.line_properties.spacing * ' ').join(specs)


def test(items=None, spacing=2, max_line_width=80, sort_items=True):
    if items is None:
        items = globals().keys()
    if sort_items:
        items = sorted(items, key=str.lower)
    print(columnize(items, spacing, max_line_width))
