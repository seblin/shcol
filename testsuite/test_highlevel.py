import functools
import os
import shcol
import unittest

class PrintFunctionTestCase(unittest.TestCase):
    def __getattr__(self, name):
        if name.startswith('print_') and hasattr(shcol, name):
            func = getattr(shcol, name)
            return functools.partial(func, print_stream=self.pseudo_stream)
        return object.__getattr__(self, name)

    def setUp(self):
        self.pseudo_stream = shcol.helpers.StringIO()

    def tearDown(self):
        self.pseudo_stream = None

    def get_output(self):
        return self.pseudo_stream.getvalue()

class PrintColumnizedTest(PrintFunctionTestCase):
    def test_items(self):
        items = ['spam', 'ham', 'eggs']
        expected = '  '.join(items) + '\n'
        self.print_columnized(items)
        self.assertEqual(self.get_output(), expected)

    def test_no_items(self):
        self.print_columnized([])
        self.assertEqual(self.get_output(), '\n')

class PrintAttrsTest(PrintFunctionTestCase):
    def test_print_attrs(self):
        expected = shcol.columnize(dir(shcol), sort_items=True) + '\n'
        self.print_attrs(shcol)
        self.assertEqual(self.get_output(), expected)

class PrintFilenamesTest(PrintFunctionTestCase):
    def test_get_files(self):
        expected = os.listdir('.')
        result = shcol.helpers.get_filenames(path='.', hide_dotted=False)
        self.assertEqual(result, expected)
        expected = [fn for fn in expected if not fn.startswith('.')]
        result = shcol.helpers.get_filenames(path='.', hide_dotted=True)
        self.assertEqual(result, expected)

    def test_print_filenames(self):
        filenames = os.listdir('.')
        expected = shcol.columnize(filenames, sort_items=True) + '\n'
        self.print_filenames()
        self.assertEqual(self.get_output(), expected)

    def test_hide_dotted(self):
        filenames = [fn for fn in os.listdir('.') if not fn.startswith('.')]
        expected = shcol.columnize(filenames, sort_items=True) + '\n'
        self.print_filenames(hide_dotted=True)
        self.assertEqual(self.get_output(), expected)
