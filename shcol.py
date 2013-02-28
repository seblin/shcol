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
    line_properties = LinePropertyBuilder(
                        items, spacing, max_line_width).get_properties()
    formatter = Formatter(line_properties, items)
    return '\n'.join(formatter.line_strings)

class LinePropertyBuilder(object):
    def __init__(self, items, spacing=2, max_line_width=80):
        self.item_widths = [len(item) for item in items]
        self.spacing = spacing
        self.max_line_width = max_line_width

    def get_properties(self):
        column_widths, num_lines = self._calculate_columns()
        return LineProperties(column_widths, self.spacing, num_lines)

    def _calculate_columns(self):
        self._check_values()
        if not self.item_widths:
            return [], 0
        if any(width > self.max_line_width for width in self.item_widths):
            return [self.max_line_width], len(self.item_widths)
        return self._find_positionings()

    def _check_values(self):
        for value in (self.spacing, self.max_line_width):
            if not isinstance(value, int) or value < 0:
                msg = 'spacing and max_line_width must be non-negative integers'
                raise ValueError(msg)

    def _find_positionings(self):
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
                return column_widths, chunk_size


class Formatter(object):
    def __init__(self, line_properties, items=[]):
        self.line_properties = line_properties
        self.items = items

    @property
    def line_strings(self):
        chunk_size = self.line_properties.num_lines
        template = self.get_line_template()
        for i in _range(chunk_size):
            line_items = tuple(self.items[i::chunk_size])
            try:
                yield template % line_items
            except TypeError:
                # number of specs != len(line_items)
                # -> re-generate template
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
