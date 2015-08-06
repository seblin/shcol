# -*- coding: utf-8 -*-
# Copyright (c) 2013-2015, Sebastian Linke

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
        stdout=config.TERMINAL_STREAM, stderr=config.ERROR_STREAM
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
            'Columize and sort:\n'
            '%(prog)s -S foo bar baz\n\n'
            'Columnize command output on Linux (Debian):\n'
            '%(prog)s -S -c0 < /proc/modules\n'
            'dpkg --get-selections \'python3*\' | %(prog)s -c0 -s4\n\n'
            'Columnize process names on Windows PowerShell:\n'
            '(ps).name | %(prog)s -U'
        )
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.init_arguments()

    def print_message(self, message, stream=None):
        """
        Print `message` to `stream`.

        If `stream` is `sys.stdout` or `sys.stderr` then it is translated to its
        corresponding instance variable (`self.stdout` or `self.stderr`).

        This technique makes it possible to control the output streams of some
        internal methods defined by the superclass. Most of them do not support
        setting alternative streams directly. Instead, they invoke methods that
        are based on `_print_message()`. By redefining that method, which does
        expect the stream to be used as a parameter, the new implementation is
        able to map those stream references to alternative streams.

        Note that the actual work is done by `_print_message`. The "public"
        version of it (`print_message`) is used a thin wrapper around it.
        """
        self._print_message(message, stream)

    def _print_message(self, message, stream):
        """
        Redefined internal method called by the superclass. See docstring of
        `print_message()` for details.
        """
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
            '-c', '--column', metavar='N', type=helpers.num, dest='column',
            help='choose a specific column per line via an index value\n'
                 '(indices start at 0, column separator is whitespace)\n'
                 'will only work when items are supplied via stdin'
        )
        self.add_argument(
            '-F', '--filter', metavar='P', dest='pattern',
            help='only columnize items which match the pattern P\n'
                 '(P should include wildcard symbols such as "?" or "*")'
        )
        self.add_argument(
            '-S', '--sort', action='store_true', default=config.SORT_ITEMS,
            help='sort the items'
        )
        self.add_argument(
            '-U', '--unique', action='store_true', default=config.MAKE_UNIQUE,
            help='process only the first occurrence of an item\n'
                 '(i.e. doublets are eliminated)'
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
        this is a redefined method of `argparse.ArgumentParser`.
        """
        args = argparse.ArgumentParser.parse_args(self, args, namespace)
        if args.items and args.column is not None:
            self.error('can\'t use --column when items are given as arguments')
        if not args.items:
            args.items = helpers.get_lines(self.stdin)
            if args.column is not None:
                args.items = helpers.get_column(args.column, args.items)
            args.items = list(args.items)
        return args

def main(args=None, prog_name='shcol', version=__version__):
    """
    Parse command-line arguments and invoke `highlevel.print_columnized()`
    with the result.

    `args` defines the arguments to parse. If this is `None` then `sys.argv[1:]`
    is used instead.

    `prog_name` defines the program name to use for the help text.

    `version` should be a string containing the program's version.

    If an exception occurs during running this function then its message (if
    any) will be written to standard error and the interpreter is requested to
    shut down (i.e. it exits with an error code if `SystemExit` is not caught).
    """
    parser = ArgumentParser(prog_name, version)
    try:
        args = parser.parse_args(args)
        highlevel.print_columnized(
            args.items, spacing=args.spacing, line_width=args.width,
            pattern=args.pattern, make_unique=args.unique, sort_items=args.sort
        )
    except KeyboardInterrupt:
        parser.exit(1)
    except Exception as exc:
        parser.error(exc)
