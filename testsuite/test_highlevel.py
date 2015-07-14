# -*- coding: utf-8 -*-
# Copyright (c) 2013-2015, Sebastian Linke

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
            return functools.partial(func, output_stream=self.pseudo_stream)
        return unittest.TestCase.__getattr__(self, name)

    def setUp(self):
        self.pseudo_stream = shcol.helpers.StringIO()

    def get_output(self):
        return self.pseudo_stream.getvalue().rstrip('\n')

class PrintColumnizedTest(PrintFunctionTestCase):
    def test_items(self):
        items = ['spam', 'ham', 'eggs']
        expected = '  '.join(items)
        self.print_columnized(items, line_width=80)
        self.assertEqual(self.get_output(), expected)

    def test_no_items(self):
        self.print_columnized([], line_width=80)
        self.assertEqual(self.get_output(), '')

class PrintAttrNamesTest(PrintFunctionTestCase):
    def test_print_attr_names(self):
        expected = shcol.columnize(dir(shcol), line_width=80, sort_items=True)
        self.print_attr_names(shcol, line_width=80)
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
        expected = [
            os.path.join(module_path, filename)
            for filename in expected if filename.endswith('.py')
        ]
        pattern = os.path.join(module_path, '*.py')
        result = list(shcol.helpers.get_filenames(pattern))
        self.assertEqual(expected, result)

    def test_print_filenames(self):
        filenames = os.listdir('.')
        expected = shcol.columnize(filenames, line_width=80, sort_items=True)
        self.print_filenames(line_width=80)
        self.assertEqual(expected, self.get_output())
