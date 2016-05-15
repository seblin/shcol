# -*- coding: utf-8 -*-
# Copyright (c) 2013-2016, Sebastian Linke

# Released under the Simplified BSD license
# (see LICENSE file for details).

import functools
import os
import shcol
import unittest

class PrintFunctionTestCase(unittest.TestCase):
    def __getattr__(self, name):
        if name.startswith('print_') and hasattr(shcol, name):
            func = getattr(shcol, name)
            return functools.partial(func, **self.options)
        return unittest.TestCase.__getattribute__(self, name)

    def setUp(self):
        self.pseudo_stream = shcol.helpers.StringIO()
        self.options = {'line_width': 80, 'output_stream': self.pseudo_stream}
        self.items = ['spam', 'ham', 'eggs']

    def columnize(self, items, **options):
        new_options = self.options.copy()
        new_options.update(options)
        return shcol.columnize(items, **new_options)

    def get_output(self):
        return self.pseudo_stream.getvalue().rstrip('\n')

class PrintColumnizedTest(PrintFunctionTestCase):
    def test_items(self):
        expected = '  '.join(self.items)
        self.print_columnized(self.items)
        self.assertEqual(self.get_output(), expected)

    def test_no_items(self):
        self.print_columnized([])
        self.assertEqual(self.get_output(), '')

class PrintSortedTest(PrintFunctionTestCase):
    def test_items(self):
        expected = self.columnize(self.items, sort_items=True)
        self.print_sorted(self.items)
        self.assertEqual(self.get_output(), expected)

    def test_spacing(self):
        expected = self.columnize(self.items, spacing=5, sort_items=True)
        self.print_sorted(self.items, spacing=5)
        self.assertEqual(self.get_output(), expected)

class PrintFilenamesTest(PrintFunctionTestCase):
    def test_get_filenames(self):
        expected = os.listdir('.')
        result = list(shcol.helpers.get_filenames())
        self.assertEqual(result, expected)
        module_path = os.path.abspath(os.path.dirname(__file__))
        result = list(shcol.helpers.get_filenames(module_path))
        expected = os.listdir(module_path)
        self.assertEqual(result, expected)
        expected = [fn for fn in expected if fn.endswith('.py')]
        pattern = os.path.join(module_path, '*.py')
        result = list(shcol.helpers.get_filenames(pattern))
        self.assertEqual(expected, result)

    def test_print_filenames(self):
        filenames = os.listdir('.')
        expected = shcol.columnize(filenames, line_width=80, sort_items=True)
        self.print_filenames()
        self.assertEqual(expected, self.get_output())
