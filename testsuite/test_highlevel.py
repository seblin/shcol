import unittest
import shcol

from _helpers import CapturedStream

class PrintTestBase(unittest.TestCase):
    def get_result(self, func, *args, **kwargs):
        with CapturedStream('stdout') as outstream:
            func(*args, **kwargs)
            return outstream.getvalue()

class PrintColumnizedTest(PrintTestBase):
    def test_items(self):
        items = ['spam', 'ham', 'eggs']
        expected = '  '.join(items) + '\n'
        result = self.get_result(shcol.print_columnized, items)
        self.assertEqual(result, expected)

    def test_no_items(self):
        result = self.get_result(shcol.print_columnized, [])
        self.assertEqual(result, '\n')

class PrintAttrsTest(PrintTestBase):
    def test_print_attrs(self):
        expected = shcol.columnize(dir(shcol), sort_items=True) + '\n'
        result = self.get_result(shcol.print_attrs, shcol)
        self.assertEqual(result, expected)
