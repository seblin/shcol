#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import functools
import locale
import shcol
import unittest


class TestColumnize(unittest.TestCase):
    def _columnize(self, *args, **kwargs):
        return shcol.columnize(*args, **kwargs)

    def _join(self, items, spacing=2):
        return (spacing * ' ').join(items)

    def _sorted(self, items, locale_to_use=None):
        if locale_to_use is None:
            return sorted(items)
        old_locale = locale.getlocale(locale.LC_COLLATE)
        sortkey = functools.cmp_to_key(locale.strcoll)
        try:
            locale.setlocale(locale.LC_COLLATE, locale_to_use)
            return sorted(items, key=sortkey)
        finally:
            locale.setlocale(locale.LC_COLLATE, old_locale)

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

    def test_sort_items(self):
        items = ['spam', 'ham', 'egg', 'foo', 'bar', 'baz']
        self.assertEqual(
            self._columnize(items, sort_items=True),
            self._join(self._sorted(items))
        )
        items = ['spam', 'häm', 'egg', 'späm', 'ham', 'ägg']
        german_locale = ('de_DE', 'UTF-8')
        self.assertEqual(
            self._columnize(items, sort_items=True),
            self._join(self._sorted(items, german_locale))
        )
        

if __name__ == '__main__':
    unittest.main(verbosity=2)
