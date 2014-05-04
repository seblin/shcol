import unittest
import shcol

from _helpers import CapturedStream

class PrintColumnizedTest(unittest.TestCase):
    def _get_result(self, items):
        with CapturedStream('stdout') as outstream:
            shcol.print_columnized(items)
            return outstream.getvalue()
        
    def test_items(self):
        items = ['spam', 'ham', 'eggs']
        expected = '  '.join(items) + '\n'
        self.assertEqual(self._get_result(items), expected)

    def test_no_items(self):
        self.assertEqual(self._get_result([]), '\n')

class PrintAttrsTest(unittest.TestCase):
    def test_print_attrs(self):
        expected = shcol.columnize(dir(shcol), sort_items=True) + '\n'
        with CapturedStream('stdout') as outstream:
            shcol.print_attrs(shcol)
            result = outstream.getvalue()
            self.assertEqual(result, expected)
