import unittest
import os
import shcol

class PrintTestBase(unittest.TestCase):
    def get_output(self, func, *args, **kwargs):
        with shcol.helpers.CapturedStream('stdout') as outstream:
            func(*args, **kwargs)
            return outstream.getvalue()

class PrintColumnizedTest(PrintTestBase):
    def test_items(self):
        items = ['spam', 'ham', 'eggs']
        expected = '  '.join(items) + '\n'
        result = self.get_output(shcol.print_columnized, items)
        self.assertEqual(result, expected)

    def test_no_items(self):
        result = self.get_output(shcol.print_columnized, [])
        self.assertEqual(result, '\n')

class PrintAttrsTest(PrintTestBase):
    def test_print_attrs(self):
        expected = shcol.columnize(dir(shcol), sort_items=True) + '\n'
        result = self.get_output(shcol.print_attrs, shcol)
        self.assertEqual(result, expected)

class PrintFilesTest(PrintTestBase):
    def test_get_files(self):
        # TODO: Make this test smarter
        expected = os.listdir('.')
        result = shcol.helpers.get_files('.', False)
        self.assertEqual(result, expected)
        expected = [fn for fn in expected if not fn.startswith('.')]
        result = shcol.helpers.get_files('.', True)
        self.assertEqual(result, expected)

    def test_print_files(self):
        filenames = os.listdir('.')
        expected = shcol.columnize(filenames, sort_items=True) + '\n'
        result = self.get_output(shcol.print_files)
        self.assertEqual(result, expected)
        filenames = [fn for fn in filenames if not fn.startswith('.')]
        expected = shcol.columnize(filenames, sort_items=True) + '\n'
        result = self.get_output(shcol.print_files, hide_dotted=True)
        self.assertEqual(result, expected)
