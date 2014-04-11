import shcol
import sys
import unittest

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

DUMMY_ITEM = 'spam'

class ArgumentParserTest(unittest.TestCase):
    def setUp(self):
        self.parser = shcol.cli.ArgumentParser('shcol', shcol.__version__)

    def _get_stderr_output(self, args):
        old_stderr = sys.stderr
        sys.stderr = StringIO()
        result = ''
        try:
            self.parser.parse_args(args)
        except SystemExit:
            result = sys.stderr.getvalue().rstrip('\n')
        finally:
            sys.stderr = old_stderr
        return result

    def test_version(self):
        expected = '{} {}'.format('shcol', shcol.__version__)
        for version in ('--version', '-v'):
            result = self._get_stderr_output([version])
            self.assertEqual(result, expected)

    def _test_num_option(self, long_option, short_option):
        option_name = long_option.lstrip('-')
        dummy_item = 'spam'
        for value in ('0', '2', '80', '100'):
            args = self.parser.parse_args([long_option, value, DUMMY_ITEM])
            self.assertEqual(getattr(args, option_name), int(value))
        for invalid in ('-42', '-1', '1.0', 'x'):
            error = self._get_stderr_output([long_option, invalid, DUMMY_ITEM])
            self.assertIn('invalid num value', error)
        args = self.parser.parse_args([short_option, '2', DUMMY_ITEM])
        self.assertEqual(getattr(args, option_name), 2)

    def test_spacing(self):
        self._test_num_option('--spacing', '-s')

    def test_line_width(self):
        self._test_num_option('--width', '-w')

    def test_items(self):
        items = ['spam', 'ham', 'egg']
        args = self.parser.parse_args(items)
        self.assertEqual(args.items, items)

    def test_sort(self):
        args = self.parser.parse_args([DUMMY_ITEM])
        self.assertFalse(args.sort)
        args = self.parser.parse_args(['--sort', DUMMY_ITEM])
        self.assertTrue(args.sort)
