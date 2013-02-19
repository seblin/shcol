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
    line_properties = get_line_properties(items, spacing, max_line_width)
    formatter = Formatter(line_properties, items)
    return '\n'.join(formatter.line_strings)

def get_line_properties(items, spacing, max_line_width):
    for value in (spacing, max_line_width):
        if not isinstance(value, int) or value < 0:
            msg = 'spacing and max_line_width must be non-negative integers'
            raise ValueError(msg)
    item_widths = [len(item) for item in items]
    if not item_widths:
        return LineProperties([], spacing)
    if max(item_widths) >= max_line_width:
        return LineProperties([max_line_width], spacing)
    num_items = len(item_widths)
    for chunk_size in count(1):
        column_widths = [max(item_widths[i : i + chunk_size])
                         for i in _range(0, num_items, chunk_size)]
        line_width = sum(column_widths) + (len(column_widths) - 1) * spacing
        if line_width <= max_line_width:
            break
    return LineProperties(column_widths, spacing)

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

    def get_line_template(self, num_specs=-1):
        if num_specs < 0:
            num_specs = self.num_columns
        if num_specs == 0:
            return ''
        if num_specs == 1:
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
