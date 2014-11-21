# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014, Sebastian Linke

# Released under the Simplified BSD license
# (see LICENSE file for details).

from __future__ import unicode_literals

import shcol
import sys
import unittest

class ColumnizeTest(unittest.TestCase):

    @staticmethod
    def columnize(items, spacing=2, line_width=80, sort_items=False):
        return shcol.columnize(items, spacing, line_width, sort_items)

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

    def test_sort_items(self):
        # TODO: Test for more languages (currently only german Umlauts)
        items = ['spam', 'ham', 'äggs', 'fü', 'bar', 'baz']
        result = self.columnize(items, sort_items=True)
        expected = self.join(shcol.helpers.get_sorted(items))
        self.assertEqual(result, expected)

    def test_invalid_values(self):
        with self.assertRaises(TypeError):
            self.columnize([42])
            self.columnize(['spam'], spacing='bogus')
            self.columnize(['spam'], line_width='bogus')
        with self.assertRaises(ValueError):
            self.columnize(['spam'], spacing=-42)
            self.columnize(['spam'], line_width=-42)


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
            ([100 * 'spam', 100 * 'ham', 100 * 'eggs'], ([400], 3)),
            ([30 * 'x', 10 * 'y', 15 * 'ä'], ([30, 10, 15], 1)),
            ([50 * 'a', 40 * 'b', 30 * 'c'], ([50], 3)),
            ([50 * 'a', 40 * 'b', 28 * 'c'], ([50, 28], 2)),
        ]

    def make_line_properties(self, item_widths, num_lines, spacing=2):
        return shcol.core.LineProperties(item_widths, spacing, num_lines)

    def test_get_properties(self):
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

    def test_line_width_getter(self):
        try:
            expected = shcol.helpers.get_terminal_width()
        except (IOError, OSError):
            expected = shcol.config.LINE_WIDTH_FALLBACK
        self.assertEqual(self.calculator.line_width, expected)
        self.calculator.line_width = 40
        self.assertEqual(self.calculator.line_width, 40)

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
        self.assertEqual(self.calculator.calculate_columns([81]), ([81], 1))
        self.calculator.allow_exceeding = False
        with self.assertRaises(ValueError):
            self.calculator.calculate_columns([81])

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
        item_widths = [234, 23, 246]
        expected = [([234, 23, 246], 1), ([234, 246], 2), ([246], 3)]
        result = self.calculator.get_column_configs(
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
            result = self.calculator.get_widths_and_lines(
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


class FormatterTest(unittest.TestCase):
    def setUp(self):
        calc = shcol.core.ColumnWidthCalculator(spacing=2, line_width=80)
        self.formatter = shcol.core.IterableFormatter(calc)

    def join(self, items):
        return '  '.join(items)

    def test_format(self):
        for items in (
            [], ['spam', 'ham', 'egg'], ['späm', 'häm', 'ägg']
        ):
            self.assertEqual(self.formatter.format(items), self.join(items))

    def make_lines(self, items):
        return list(self.formatter.make_lines(items))

    def test_make_lines(self):
        items = ['foo', 'bar', 'baz']
        lines = self.make_lines(items)
        self.assertEqual(lines, [self.join(items)])
        self.formatter.calculator.line_width = 3
        self.assertEqual(self.make_lines(items), items)
        items = [60 * 'ä', 40 * 'ö']
        expected = [60 * 'ä', 40 * 'ö']
        self.formatter.calculator.line_width = 50
        self.assertEqual(self.make_lines(items), expected)
        self.formatter.calculator.allow_exceeding = False
        self.assertRaises(ValueError, self.make_lines, items)

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
