import shcol
import sys
import unittest

class ArgumentParserTest(unittest.TestCase):
    def setUp(self):
        self.parser = shcol.cli.ArgumentParser('shcol', shcol.__version__)

    def _get_stderr_output(self, args):
        result = ''
        with shcol.helpers.CapturedStream('stderr') as errstream:
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

    def test_default_params(self):
        args = self.parser.parse_args(['spam'])
        self.assertEqual(args.spacing, 2)
        self.assertEqual(args.width, None)

    def test_no_item_args(self):
        with shcol.helpers.CapturedStream('stdin') as instream:
            args = self.parser.parse_args([])
            self.assertFalse(args.items)
            instream.write('spam\nham\neggs')
            instream.seek(0)
            args = self.parser.parse_args([])
            self.assertEqual(args.items, ['spam', 'ham', 'eggs'])

    def test_column_option(self):
        self._test_num_option_invalid('-c', '--column')
        with shcol.helpers.CapturedStream('stdin') as instream:
            instream.write('xxx spam\nzzz ham\n~~~ eggs')
            instream.seek(0)
            args = self.parser.parse_args(['-c' '1'])
            self.assertEqual(args.items, ['spam', 'ham', 'eggs'])
            instream.seek(0)
            error = self._get_stderr_output(['-c', '42'])
            self.assertIn('failed to fetch data', error)

    def test_sort_option(self):
        args = self.parser.parse_args(['spam'])
        self.assertFalse(args.sort)
        args = self.parser.parse_args(['--sort', 'spam'])
        self.assertTrue(args.sort)
