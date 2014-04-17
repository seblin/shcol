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
    dummy_item = 'spam'

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

    def _test_num_option(self, long_option, short_option):
        option_name = long_option.lstrip('-')
        dummy_item = 'spam'
        for value in ('0', '2', '80', '100'):
            args = self.parser.parse_args([long_option, value, self.dummy_item])
            self.assertEqual(getattr(args, option_name), int(value))
        for invalid in ('-42', '-1', '1.0', 'x'):
            error = self._get_stderr_output(
                [long_option, invalid, self.dummy_item]
            )
            self.assertIn('invalid num value', error)
        args = self.parser.parse_args([short_option, '2', self.dummy_item])
        self.assertEqual(getattr(args, option_name), 2)

    def test_spacing(self):
        self._test_num_option('--spacing', '-s')

    def test_line_width(self):
        self._test_num_option('--width', '-w')

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

    def test_sort(self):
        args = self.parser.parse_args([self.dummy_item])
        self.assertFalse(args.sort)
        args = self.parser.parse_args(['--sort', self.dummy_item])
        self.assertTrue(args.sort)
