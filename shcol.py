from __future__ import print_function

from collections import namedtuple
from itertools import count

try:
    _range = xrange
except NameError:
    _range = range

LineProperties = namedtuple(
                   'LineProperties', 'column_widths, spacing, num_lines')

def columnize(items, spacing=2, max_line_width=80):
    property_builder = LinePropertyBuilder(spacing, max_line_width)
    formatter = Formatter(property_builder)
    return '\n'.join(formatter.get_line_strings(items))


class LinePropertyBuilder(object):
    def __init__(self, spacing=2, max_line_width=80):
        self.spacing = spacing
        self.max_line_width = max_line_width

    def get_properties(self, items):
        self._check_values()
        item_widths = [len(item) for item in items]
        if not item_widths:
            column_widths, num_lines = [], 0
        elif any(width > self.max_line_width for width in item_widths):
            column_widths, num_lines = [self.max_line_width], len(item_widths)
        else:
            column_widths, num_lines = self._calculate_columns(item_widths)
        return LineProperties(column_widths, self.spacing, num_lines)

    def _check_values(self):
        for value in (self.spacing, self.max_line_width):
            if not isinstance(value, int) or value < 0:
                msg = 'spacing and max_line_width must be non-negative integers'
                raise ValueError(msg)

    def _calculate_columns(self, item_widths):
        num_items = len(item_widths)
        for chunk_size in count(1):
            column_widths = []
            line_width = -self.spacing
            for i in _range(0, num_items, chunk_size):
                column_width = max(item_widths[i : i + chunk_size])
                line_width += column_width + self.spacing
                if line_width > self.max_line_width:
                    break
                column_widths.append(column_width)
            else:
                return column_widths, chunk_size


class Formatter(object):
    def __init__(self, property_builder=LinePropertyBuilder(),
                       allow_exceeding=True):
        self.property_builder = property_builder
        self.allow_exceeding = allow_exceeding

    def get_line_strings(self, items):
        properties = self.property_builder.get_properties(items)
        column_widths = properties.column_widths
        chunk_size = properties.num_lines
        template = self.get_line_template(column_widths)
        for i in _range(chunk_size):
            line_items = tuple(items[i::chunk_size])
            try:
                yield template % line_items
            except TypeError:
                # number of specs != len(line_items)
                # -> re-generate template
                line_size = len(line_items)
                template = self.get_line_template(column_widths[:line_size])
                yield template % line_items

    def get_line_template(self, column_widths):
        if not column_widths:
            return ''
        if len(column_widths) == 1 and self.allow_exceeding:
            return '%s'
        specs = ['%%-%d.%ds' % (width, width) for width in column_widths[:-1]]
        specs.append('%%.%ds' % column_widths[-1])
        return (self.property_builder.spacing * ' ').join(specs)


def test(items=None, spacing=2, max_line_width=80, sort_items=True):
    if items is None:
        items = globals().keys()
    if sort_items:
        items = sorted(items, key=str.lower)
    print(columnize(items, spacing, max_line_width))
