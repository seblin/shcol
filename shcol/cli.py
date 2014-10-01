# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014, Sebastian Linke

# Released under the Simplified BSD license
# (see LICENSE file for details).

"""
The command-line interface for `shcol`.
"""

import argparse
import sys

from . import __version__, config, helpers, highlevel

__all__ = ['main']

class ArgumentParser(argparse.ArgumentParser):
    """
    Implementation for generating help text and command-line parsing.
    """
    def __init__(
        self, prog_name, version, stdin=config.INPUT_STREAM,
        stdout=config.OUTPUT_STREAM, stderr=config.ERROR_STREAM
    ):
        """
        Initialize the parser.

        `prog_name` defines the program name used when displaying information.

        `version` should be a string containing the program's version.

        `stdin`, `stdout` and `stderr` are the streams to use. They should be
        file-like objects defining at least a `.read()` and a `.write()` method.
        """
        self.version_string = '{} {}'.format(prog_name, version)
        argparse.ArgumentParser.__init__(
            self, prog=prog_name, formatter_class=argparse.RawTextHelpFormatter,
            description='Generate columnized output for given string items.\n\n'
            'Examples (on a Debian system):\n'
            '\n'
            '%(prog)s -S foo bar baz\n'
            '%(prog)s -S -c0 < /proc/modules\n'
            'dpkg --get-selections \'python3*\' | %(prog)s -c0 -s4'
        )
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.init_arguments()

    def _print_message(self, message, stream=None):
        if stream is sys.stdout:
            stream = self.stdout
        elif stream is sys.stderr:
            stream = self.stderr
        argparse.ArgumentParser._print_message(self, message, file=stream)

    def init_arguments(self):
        """
        Argument names and the whole CLI-syntax are defined by this method.
        """
        self.add_argument(
            'items', nargs='*', metavar='item',
            help='an item to columnize\n'
                 '(read from stdin if item arguments are not present)'
        )
        self.add_argument(
            '-s', '--spacing', metavar='N', type=helpers.num,
            default=config.SPACING,
            help='number of blanks between two columns (default: {})'
                 .format(config.SPACING)
        )
        self.add_argument(
            '-w', '--width', metavar='N', type=helpers.num,
            help='maximal amount of characters per line\n'
                 '(use terminal width by default)'
        )
        self.add_argument(
            '-S', '--sort', action='store_true', default=False,
            help='sort the items'
        )
        self.add_argument(
            '-c', '--column', metavar='N', type=helpers.num, dest='column',
            help='choose a specific column per line via an index value\n'
                 '(indices start at 0, column seperator is whitespace)'
        )
        self.add_argument(
            '-v', '--version', action='version', version=self.version_string
        )

    def parse_args(self, args=None, namespace=None):
        """"
        Parse given arguments and return a Namespace-object that represents the
        result of parsing.

        `args` should be a sequence of strings. If this is `None`, then
        `sys.argv` is used instead.

        `namespace` defines the Namespace to use. If this is `None`, then a new
        Namespace is created.

        See the stdlib's `argparse`-module documentation for more details, since
        this is an overriden method of `argparse.ArgumentParser`.
        """
        args = argparse.ArgumentParser.parse_args(self, args, namespace)
        if not args.items:
            args.items = helpers.get_lines(self.stdin)
        if args.column is not None:
            args.items = helpers.get_column(args.column, args.items)
        try:
            # Walk through the iterator
            args.items = list(args.items)
        except IndexError:
            msg = 'failed to fetch input for column at index {}'
            self.error(msg.format(args.column))
        except KeyboardInterrupt:
            self.exit(1)
        return args

def main(args=None, prog_name='shcol', version=__version__):
    """
    Parse command-line arguments and invoke `shcol.print_columnized()` with the
    result.

    `args` defines the arguments to parse. If this is `None` then `sys.argv[1:]`
    is used instead.

    `prog_name` defines the program name to use for the help text.

    `version` should be a string containing the program's version.
    """
    parser = ArgumentParser(prog_name, version)
    args = parser.parse_args(args)
    try:
        highlevel.print_columnized(
            args.items, spacing=args.spacing,
            line_width=args.width, sort_items=args.sort
        )
    except UnicodeEncodeError:
        parser.error('failed to encode input')
