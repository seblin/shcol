# -*- coding: utf-8 -*-
# Copyright (c) 2013-2015, Sebastian Linke

# Released under the Simplified BSD license
# (see LICENSE file for details).

from __future__ import unicode_literals

import shcol
import unittest

class ColumnizeTest(unittest.TestCase):

    @staticmethod
    def columnize(items, line_width=80, **options):
        return shcol.columnize(items, line_width=line_width, **options)

    @staticmethod
    def join(items, spacing=2):
        return (spacing * ' ').join(items)

    def test_no_items(self):
        self.assertEqual(self.columnize([]), '')

    def test_spacing(self):
        items = ['foo', 'bar', 'baz']
        for i in range(3):
            self.assertEqual(
                self.columnize(items, spacing=i), self.join(items, i)
            )

    def test_line_width(self):
        x, y, ae = 30 * 'x', 10 * 'y', 15 * 'ä'
        items = [x, y, ae]
        self.assertEqual(
            self.columnize(items), self.join(items)
        )
        self.assertEqual(
            self.columnize(items, line_width=50),
            '%s\n%s' % (self.join([x, ae]), y)
        )
        self.assertEqual(
            self.columnize(items, line_width=45), '\n'.join(items)
        )

    def test_make_unique(self):
        items = ['spam', 'spam', 'ham', 'ham', 'ham', 'eggs']
        result = self.columnize(items, make_unique=True)
        expected = self.join(['spam', 'ham', 'eggs'])
        self.assertEqual(result, expected)

    def test_sort_items(self):
        items = ['spam', 'ham', 'eggs']
        result = self.columnize(items, sort_items=True)
        expected = self.join(['eggs', 'ham', 'spam'])
        self.assertEqual(result, expected)

    def test_invalid_values(self):
        with self.assertRaises(ValueError):
            items = ['spam']
            for invalid in ('bogus', -42):
                self.columnize(items, spacing=invalid)
                self.columnize(items, line_width=invalid)


class ColumnWidthCalculatorTest(unittest.TestCase):
    def setUp(self):
        self.calculator = shcol.core.ColumnWidthCalculator(
            spacing=2, line_width=80
        )
        self.expected_results = [
            ([], ([], 0)),
            ([''], ([0], 1)),
            ([' '], ([1], 1)),
            (['spam', 'ham', 'eggs'], ([4, 3, 4], 1)),
            ([30 * 'x', 10 * 'y', 15 * 'ä'], ([30, 10, 15], 1)),
            ([50 * 'a', 40 * 'b', 30 * 'c'], ([50], 3)),
            ([50 * 'a', 40 * 'b', 28 * 'c'], ([50, 28], 2)),
        ]

    def make_line_properties(self, item_widths, num_lines, spacing=2):
        return shcol.core.LineProperties(item_widths, spacing, num_lines)

    def test_get_line_properties(self):
        for items, props in self.expected_results:
            self.assertEqual(
                self.calculator.get_line_properties(items),
                self.make_line_properties(*props)
            )

    def test_small_line_width(self):
        self.calculator.line_width = 45
        self.assertEqual(
            self.calculator.get_line_properties([30 * 'x', 10 * 'y', 15 * 'ä']),
            self.make_line_properties([30], 3)
        )

    def test_wide_spacing(self):
        self.calculator.spacing = 5
        for items, props in self.expected_results[:-1]:
            self.assertEqual(
                self.calculator.get_line_properties(items),
                self.make_line_properties(*props, spacing=5)
            )
        self.assertEqual(
            self.calculator.get_line_properties([50 * 'a', 40 * 'b', 28 * 'c']),
            self.make_line_properties([50], 3, spacing=5)
        )

    def test_calculate_columns(self):
        for items, result in self.expected_results:
            item_widths = [len(item) for item in items]
            self.assertEqual(
                self.calculator.calculate_columns(item_widths), result
            )
        self.calculator.line_width = 45
        self.assertEqual(
            self.calculator.calculate_columns([30, 10, 15]), ([30], 3)
        )

    def test_allow_exceeding(self):
        with self.assertRaises(shcol.core.LineTooSmallError):
            self.calculator.calculate_columns([81])
        self.calculator.allow_exceeding = True
        self.assertEqual(self.calculator.calculate_columns([81]), ([81], 1))

    def test_calculate_max_columns(self):
        expected_results = [
            ([], 0), ([0], 1), ([1], 1), ([81], 1), ([81, 2], 1), ([79, 2], 1),
            ([20, 19, 18], 3), ([70] + [0] * 100, 6), ([70] + [1] * 100, 4),
            ([70, 1, 2, 3], 4)
        ]
        for item_widths, result in expected_results:
            self.assertEqual(
                self.calculator.calculate_max_columns(item_widths), result
            )

    def test_get_column_configs(self):
        item_widths = [2, 347, 65, 32, 345, 23]
        expected = [
            ([2, 347, 65, 32, 345, 23], 1),
            ([347, 65, 345], 2),
            ([347, 345], 3),
            ([347], 6),
        ]
        result = self.calculator.iter_column_configs(
            item_widths, len(item_widths)
        )
        self.assertEqual(list(result), expected)

    def test_get_widths_and_lines(self):
        item_widths = [2, 347, 65, 32, 345, 23]
        expected_results = [
            ([2, 347, 65, 32, 345, 23], 1),
            ([347, 65, 345], 2),
            ([347, 65, 345], 2),
            ([347, 65, 345], 2),
            ([347, 345], 3),
            ([347], 6),
        ]
        column_range = range(len(expected_results), 0, -1)
        for num_columns, expected in zip(column_range, expected_results):
            result = self.calculator.get_unchecked_column_config(
                item_widths, num_columns
            )
            self.assertEqual(result, expected)

    def fits(self, item_widths):
        return self.calculator.fits_in_line(item_widths)

    def test_fits_in_line(self):
        for item_widths in ([], [0], [1], [11, 20, 10, 13], [0, 78], [80]):
            self.assertTrue(self.fits(item_widths))
        for item_widths in ([77, 2], [70, 12], [1, 0, 78], [0, 79], [81]):
            self.assertFalse(self.fits(item_widths))
        self.calculator.spacing = 1
        self.assertTrue(self.fits([77, 2]))
        self.assertFalse(self.fits([77, 3]))
        self.calculator.line_width = 79
        self.assertFalse(self.fits([77, 2]))


class IterableFormatterTest(unittest.TestCase):
    def setUp(self):
        calc = shcol.core.ColumnWidthCalculator(spacing=2, line_width=80)
        self.formatter = shcol.core.IterableFormatter(calc)
        self.items = ['spam', 'ham', 'eggs']
        self.sorted_items = ['eggs', 'ham', 'spam']
        self.non_ascii_items = ['späm', 'häm', 'äggs']

    def join(self, items):
        return '  '.join(items)

    def test_format(self):
        for items in ([], self.items, self.non_ascii_items):
            self.assertEqual(self.formatter.format(items), self.join(items))

    def test_sort_items(self):
        self.assertEqual(
            self.formatter.format(self.items, sort_items=True),
            self.join(self.sorted_items)
        )

    def make_lines(self, items):
        return list(self.formatter.make_lines(items))

    def test_make_lines(self):
        lines = self.make_lines(self.items)
        self.assertEqual(lines, [self.join(self.items)])
        self.formatter.calculator.line_width = 4
        self.assertEqual(self.make_lines(self.items), self.items)
        items = [60 * 'ä', 40 * 'ö']
        expected = [60 * 'ä', 40 * 'ö']

        # Now test error handling
        self.formatter.calculator.line_width = 50
        with self.assertRaises(shcol.core.LineTooSmallError):
            self.make_lines(items)
        self.formatter.calculator.allow_exceeding = True
        self.assertEqual(self.make_lines(items), expected)

    def make_template(self, column_widths, spacing=2):
        props = shcol.core.LineProperties(column_widths, spacing, None)
        return self.formatter.make_line_template(props, spacing)

    def test_get_line_template(self):
        expected_results = [
            ([], ''), ([0], '%.0s'), ([42], '%.42s'),
            ([42, 13], '%-42.42s  %.13s')
        ]
        for column_widths, result in expected_results:
            self.assertEqual(self.make_template(column_widths), result)
        self.formatter.allow_exceeding = False
        expected_results = [
            ([], ''), ([0], '%.0s'), ([42], '%.42s'),
            ([42, 13], '%-42.42s  %.13s')
        ]
        for column_widths, result in expected_results:
            self.assertEqual(self.make_template(column_widths), result)
