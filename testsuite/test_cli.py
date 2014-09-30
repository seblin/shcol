import shcol
import unittest

class ArgumentParserTest(unittest.TestCase):
    def setUp(self):
        self.parser = shcol.cli.ArgumentParser('shcol', shcol.__version__)

    def get_error_message(self, args):
        error_stream = shcol.helpers.StringIO()
        self.parser.stderr = error_stream
        with self.assertRaises(SystemExit):
            self.parser.parse_args(args)
        return error_stream.getvalue().rstrip('\n')

    def test_version(self):
        expected = '{} {}'.format('shcol', shcol.__version__)
        for version in ('--version', '-v'):
            result = self.get_error_message([version])
            self.assertEqual(result, expected)

    def test_default_params(self):
        args = self.parser.parse_args(['spam'])
        self.assertEqual(args.spacing, 2)
        self.assertIsNone(args.width)
        self.assertFalse(args.sort)
        self.assertIsNone(args.column)

    def test_item_args(self):
        items = ['spam', 'ham', 'eggs']
        args = self.parser.parse_args(items)
        self.assertEqual(args.items, items)

    def test_stdin_input(self):
        self.parser.stdin = shcol.helpers.StringIO('spam\nham\neggs')
        args = self.parser.parse_args([])
        self.assertEqual(args.items, ['spam', 'ham', 'eggs'])

    def _test_num_option(self, long_option, short_option, items=['spam']):
        option_name = long_option.lstrip('-')
        for option_string in (long_option, short_option):
            for value in ('0', '2', '80', '100'):
                args = self.parser.parse_args([option_string, value] + items)
                self.assertEqual(getattr(args, option_name), int(value))
            for invalid in ('-42', '-1', '1.0', 'x'):
                error = self.get_error_message([option_string, invalid] + items)
                self.assertIn('invalid num value', error)

    def test_spacing_option(self):
        self._test_num_option('--spacing', '-s')

    def test_line_width_option(self):
        self._test_num_option('--width', '-w')

    def test_sort_option(self):
        args = self.parser.parse_args(['--sort', 'spam'])
        self.assertTrue(args.sort)

    def test_column_option(self):
        self._test_num_option('--column', '-c', items=['spam ' * 1000])

    def test_second_column(self):
        self.parser.stdin = shcol.helpers.StringIO(
            'xxx spam\nzzz ham\n~~~ eggs'
        )
        args = self.parser.parse_args(['-c' '1'])
        self.assertEqual(args.items, ['spam', 'ham', 'eggs'])

    def test_nonexistent_column(self):
        self.parser.stdin = shcol.helpers.StringIO(
            'xxx spam\nzzz ham\n~~~ eggs'
        )
        error = self.get_error_message(['-c', '42'])
        self.assertIn('failed to fetch input', error)
