# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014, Sebastian Linke

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
        self.print_columnized(items)
        self.assertEqual(self.get_output(), expected)

    def test_no_items(self):
        self.print_columnized([])
        self.assertEqual(self.get_output(), '')

class PrintAttrNamesTest(PrintFunctionTestCase):
    def test_print_attr_names(self):
        expected = shcol.columnize(dir(shcol), sort_items=True)
        self.print_attr_names(shcol)
        self.assertEqual(self.get_output(), expected)

class PrintFilenamesTest(PrintFunctionTestCase):
    def test_get_files(self):
        expected = os.listdir('.')
        result = shcol.helpers.get_filenames(path='.', hide_dotted=False)
        self.assertEqual(list(result), expected)
        expected = [fn for fn in expected if not fn.startswith('.')]
        result = shcol.helpers.get_filenames(path='.', hide_dotted=True)
        self.assertEqual(list(result), expected)

    def test_print_filenames(self):
        filenames = os.listdir('.')
        expected = shcol.columnize(filenames, sort_items=True)
        self.print_filenames()
        self.assertEqual(self.get_output(), expected)

    def test_hide_dotted(self):
        filenames = [fn for fn in os.listdir('.') if not fn.startswith('.')]
        expected = shcol.columnize(filenames, sort_items=True)
        self.print_filenames(hide_dotted=True)
        self.assertEqual(self.get_output(), expected)
