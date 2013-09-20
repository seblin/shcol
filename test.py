from __future__ import unicode_literals

import shcol
import unittest

class TestColumnize(unittest.TestCase):
    def _columnize(self, *args, **kwargs):
        return shcol.columnize(*args, **kwargs)

    def _join(self, items, spacing=2):
        return (spacing * ' ').join(items)

    def test_no_items(self):
        self.assertEqual(self._columnize([]), '')

    def test_spacing(self):
        items = ['foo', 'bar', 'baz']
        for i in range(3):
            self.assertEqual(
                self._columnize(items, spacing=i), self._join(items, i)
            )

    def test_max_line_width(self):
        x, y, z = 30 * 'x', 10 * 'y', 15 * 'z'
        items = [x, y, z]
        self.assertEqual(
            self._columnize(items), self._join([x, y, z])
        )
        self.assertEqual(
            self._columnize(items, max_line_width=50),
            '%s\n%s' % (self._join([x, z]), y)
        )
        self.assertEqual(
            self._columnize(items, max_line_width=45), '\n'.join([x, y, z])
        )


if __name__ == '__main__':
    unittest.main()
