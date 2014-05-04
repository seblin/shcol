import shcol
import sys
import unittest

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

class CapturedStream(object):
    def __init__(self, stream_name):
        self.stream_name = stream_name
        self.original_stream = getattr(sys, stream_name)
        self.pseudo_stream = StringIO()

    def __enter__(self):
        setattr(sys, self.stream_name, self.pseudo_stream)
        return self.pseudo_stream

    def __exit__(self, *unused):
        setattr(sys, self.stream_name, self.original_stream)

class ArgumentParserTest(unittest.TestCase):
    def setUp(self):
        self.parser = shcol.cli.ArgumentParser('shcol', shcol.__version__)

    def _get_stderr_output(self, args):
        result = ''
        with CapturedStream('stderr') as errstream:
            try:
                self.parser.parse_args(args)
            except SystemExit:
                result = errstream.getvalue().rstrip('\n')
        return result

    def test_version(self):
        expected = '{} {}'.format('shcol', shcol.__version__)
        for version in ('--version', '-v'):
            result = self._get_stderr_output([version])
            self.assertEqual(result, expected)

    def _test_num_option(self, long_option, short_option, *cmd_args):
        option_name = long_option.lstrip('-')
        for value in ('0', '2', '80', '100'):
            args = self.parser.parse_args([long_option, value] + list(cmd_args))
            self.assertEqual(getattr(args, option_name), int(value))
        args = self.parser.parse_args([short_option, '2'] + list(cmd_args))
        self.assertEqual(getattr(args, option_name), 2)
        self._test_num_option_invalid(short_option, long_option, *cmd_args)

    def _test_num_option_invalid(self, short_option, long_option, *cmd_args):
        for invalid in ('-42', '-1', '1.0', 'x'):
            error = self._get_stderr_output(
                [long_option, invalid] + list(cmd_args)
            )
            self.assertIn('invalid num value', error)
        error = self._get_stderr_output([short_option, '-1'] + list(cmd_args))
        self.assertIn('invalid num value', error)

    def test_spacing_option(self):
        self._test_num_option('--spacing', '-s', 'foo')

    def test_line_width_option(self):
        self._test_num_option('--width', '-w', 'foo')

    def test_item_args(self):
        items = ['spam', 'ham', 'eggs']
        args = self.parser.parse_args(items)
        self.assertEqual(args.items, items)

    def test_no_item_args(self):
        with CapturedStream('stdin') as instream:
            args = self.parser.parse_args([])
            self.assertFalse(args.items)
            instream.write('spam\nham\neggs')
            instream.seek(0)
            args = self.parser.parse_args([])
            self.assertEqual(args.items, ['spam', 'ham', 'eggs'])

    def test_column_option(self):
        self._test_num_option_invalid('-c', '--column')
        with CapturedStream('stdin') as instream:
            instream.write('xxx spam\nzzz ham\n~~~ eggs')
            instream.seek(0)
            args = self.parser.parse_args(['-c' '1'])
            self.assertEqual(args.items, ['spam', 'ham', 'eggs'])
            instream.seek(0)
            error = self._get_stderr_output(['-c', '42'])
            self.assertIn('no data to fetch', error)

    def test_sort_option(self):
        args = self.parser.parse_args(['spam'])
        self.assertFalse(args.sort)
        args = self.parser.parse_args(['--sort', 'spam'])
        self.assertTrue(args.sort)
