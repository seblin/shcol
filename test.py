#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import shcol
import unittest

class TestColumnize(unittest.TestCase):
    def _columnize(self, *args, **kwargs):
        return shcol.columnize(*args, **kwargs)

    def _join(self, items, spacing=2):
        return (spacing * ' ').join(items)

    def test_no_items(self):
        self.assertEqual(self._columnize([]), '')

    def test_spacing(self):
        items = ['foo', 'bar', 'baz']
        for i in range(3):
            self.assertEqual(
                self._columnize(items, spacing=i), self._join(items, i)
            )

    def test_max_line_width(self):
        x, y, z = 30 * 'x', 10 * 'y', 15 * 'ä'
        items = [x, y, z]
        self.assertEqual(
            self._columnize(items), self._join([x, y, z])
        )
        self.assertEqual(
            self._columnize(items, max_line_width=50),
            '%s\n%s' % (self._join([x, z]), y)
        )
        self.assertEqual(
            self._columnize(items, max_line_width=45), '\n'.join([x, y, z])
        )

    def test_sort_items(self):
        items = ['spam', 'ham', 'egg', 'foo', 'bar', 'baz']
        self.assertEqual(
            self._columnize(items, sort_items=True), self._join(sorted(items))
        )


class TestColumnWidthCalculator(unittest.TestCase):
    def setUp(self):
        self.calculator = shcol.ColumnWidthCalculator()
        self.expected_results = [
            ([], ([], 0)),
            ([''], ([0], 1)),
            ([' '], ([1], 1)),
            (['foo', 'bar', 'baz'], ([3, 3, 3], 1)),
            ([30 * 'x', 10 * 'y', 15 * 'ä'], ([30, 10, 15], 1)),
        ]

    def _make_line_properties(self, item_widths, num_lines, spacing=2):
        return shcol.LineProperties(item_widths, spacing, num_lines)

    def test_get_properties(self):
        for items, props in self.expected_results:
            self.assertEqual(
                self.calculator.get_properties(items),
                self._make_line_properties(*props)
            )
        self.calculator.max_line_width = 45
        self.assertEqual(
            self.calculator.get_properties([30 * 'x', 10 * 'y', 15 * 'ä']),
            self._make_line_properties([30], 3)
        )

    def test_calculate_columns(self):
        for items, result in self.expected_results:
            item_widths = [len(item) for item in items]
            self.assertEqual(
                self.calculator.calculate_columns(item_widths), result
            )
        self.calculator.max_line_width = 45
        self.assertEqual(
            self.calculator.calculate_columns([30, 10, 15]), ([30], 3)
        )

    def _fits(self, item_widths):
        return self.calculator.fits_in_line(item_widths)

    def test_fits_in_line(self):
        for item_widths in ([], [0], [1], [11, 20, 10, 13], [0, 78], [80]):
            self.assertTrue(self._fits(item_widths))
        for item_widths in ([77, 2], [70, 12], [1, 0, 78], [0, 79], [81]):
            self.assertFalse(self._fits(item_widths))
        self.calculator.spacing = 1
        self.assertTrue(self._fits([77, 2]))
        self.assertFalse(self._fits([77, 3]))
        self.calculator.max_line_width = 79
        self.assertFalse(self._fits([77, 2]))


if __name__ == '__main__':
    unittest.main(verbosity=2)
