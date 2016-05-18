# -*- coding: utf-8 -*-
# Copyright (c) 2013-2016, Sebastian Linke

# Released under the Simplified BSD license
# (see LICENSE file for details).

import shcol
import unittest

class CLITestMixin(object):
    def fetch_parser_output(self, args, stream_name='stdout'):
        pseudo_stream = shcol.helpers.StringIO()
        setattr(self.parser, stream_name, pseudo_stream)
        with self.assertRaises(SystemExit):
            self.parser.parse_args(args)
        return pseudo_stream.getvalue().rstrip('\n')

    def check_num_option(
        self, long_option, short_option, items=['spam'], stdin_content=None
    ):
        option_name = long_option.lstrip('-')
        for option_string in (long_option, short_option):
            for value in ('0', '2', '80', '100'):
                self.set_stdin_content(stdin_content)
                args = self.parser.parse_args([option_string, value] + items)
                self.assertEqual(getattr(args, option_name), int(value))
            for invalid in ('-42', '-1', '1.0', 'x'):
                self.set_stdin_content(stdin_content)
                args = [option_string, invalid] + items
                error = self.fetch_parser_output(args, 'stderr')
                self.assertIn('invalid num value', error)

    def set_stdin_content(self, data):
        pseudo_stream = shcol.helpers.StringIO()
        if data is not None:
            pseudo_stream.write(data)
            pseudo_stream.seek(0)
        self.parser.stdin = pseudo_stream


class ArgumentParserTest(CLITestMixin, unittest.TestCase):
    def setUp(self):
        self.parser = shcol.cli.ArgumentParser('shcol', shcol.__version__)
        self.items = ['spam', 'ham', 'eggs']

    def test_version(self):
        expected = '{} {}'.format('shcol', shcol.__version__)
        stream_name = (
            'stdout' if shcol.config.PY_VERSION >= (3, 4) else 'stderr'
        )
        for version in ('--version', '-v'):
            result = self.fetch_parser_output([version], stream_name)
            self.assertEqual(expected, result)

    def test_default_params(self):
        args = self.parser.parse_args(['spam'])
        self.assertEqual(args.spacing, 2)
        self.assertIsNone(args.width)
        self.assertIsNone(args.extra_sep)
        self.assertFalse(args.sort)
        self.assertIsNone(args.column)

    def test_item_args(self):
        args = self.parser.parse_args(self.items)
        self.assertEqual(self.items, args.items)

    def test_stdin_input(self):
        self.set_stdin_content('{}\n'.format('\n'.join(self.items)))
        args = self.parser.parse_args([])
        self.assertEqual(self.items, args.items)

    def test_spacing_option(self):
        self.check_num_option('--spacing', '-s')

    def test_line_width_option(self):
        self.check_num_option('--width', '-w')

    def test_extra_sep_option(self):
        for option in ('-e', '--extra-sep'):
            args = self.parser.parse_args([self.items, option, '|'])
            self.assertEqual('|', args.extra_sep)

    def test_unique_option(self):
        for option in ('-U', '--unique'):
            args = self.parser.parse_args([option, 'spam'])
            self.assertTrue(args.unique)

    def test_sort_option(self):
        for option in ('-S', '--sort'):
            args = self.parser.parse_args([option, 'spam'])
            self.assertTrue(args.sort)

    def test_column_option(self):
        stdin_content = 'spam ' * 1000
        self.check_num_option(
            '--column', '-c', items=[], stdin_content=stdin_content
        )

    def test_column_with_item_args(self):
        result = self.fetch_parser_output(['-c0', 'spam'], 'stderr')
        self.assertIn('can\'t use --column', result)

    def test_second_column(self):
        self.set_stdin_content('xxx spam\nzzz ham\n~~~ eggs\n')
        args = self.parser.parse_args(['-c' '1'])
        self.assertEqual(['spam', 'ham', 'eggs'], args.items)

    def test_nonexistent_column(self):
        self.set_stdin_content('xxx spam\nzzz ham\n~~~ eggs\n')
        with self.assertRaises(IndexError):
            self.parser.parse_args(['-c', '42'])


class MainFunctionTest(unittest.TestCase):
    def test_main_function(self):
        items = ['spam', 'ham', 'spam', 'eggs', 'ham']
        pseudo_stream = shcol.helpers.StringIO()
        shcol.print_columnized(
            items, spacing=4, line_width=50, sort_items=True, make_unique=True,
            extra_sep='|', output_stream=pseudo_stream
        )
        expected = pseudo_stream.getvalue().rstrip('\n')
        pseudo_stream.seek(0)
        args = items + ['-s4', '-w50', '-S', '-U', '-e=|']
        shcol.cli.main(args, output_stream=pseudo_stream)
        result = pseudo_stream.getvalue().rstrip('\n')
        self.assertEqual(expected, result)
