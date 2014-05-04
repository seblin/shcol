import unittest
import shcol

from _helpers import CapturedStream

class PrintColumnizedTest(unittest.TestCase):
    def _get_result(self, items):
        with CapturedStream('stdout') as outstream:
            shcol.print_columnized(items)
            outstream.seek(0)
            return outstream.read()
        
    def test_items(self):
        items = ['spam', 'ham', 'eggs']
        expected = '  '.join(items) + '\n'
        self.assertEqual(self._get_result(items), expected)

    def test_no_items(self):
        self.assertEqual(self._get_result([]), '\n')
