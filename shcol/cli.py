# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014, Sebastian Linke

# Released under the Simplified BSD license
# (see LICENSE file for details).

import argparse
import sys

from . import __version__, config, helpers, highlevel

__all__ = ['main']

class ArgumentParser(argparse.ArgumentParser):
    def __init__(
        self, prog_name, version, stdin=config.INPUT_STREAM,
        stdout=config.OUTPUT_STREAM, stderr=config.ERROR_STREAM
    ):
        self.version_string = '{} {}'.format(prog_name, version)
        argparse.ArgumentParser.__init__(
            self, prog=prog_name, formatter_class=argparse.RawTextHelpFormatter,
            description='Generate columnized output for given string items.\n\n'
            'Examples (on a Debian system):\n'
            '\n'
            'shcol -S foo bar baz\n'
            '(shcol -S -c0) < /proc/modules\n'
            'dpkg --get-selections \'python3*\' | shcol -c0 -s4'
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
        args = argparse.ArgumentParser.parse_args(self, args, namespace)
        if not args.items:
            try:
                args.items = list(
                    helpers.read_lines(
                        stream=self.stdin, column_index=args.column
                    )
                )
            except IndexError:
                msg = '{}: error: failed to fetch data for column at index {}'
                self.exit(1, msg.format(self.prog, args.column))
            except KeyboardInterrupt:
                self.exit(1)
        return args


def main(cmd_args=None, prog_name='shcol', version=__version__):
    parser = ArgumentParser(prog_name, version)
    args = parser.parse_args(cmd_args)
    try:
        highlevel.print_columnized(
            args.items, spacing=args.spacing,
            line_width=args.width, sort_items=args.sort
        )
    except UnicodeEncodeError:
        msg = '{}: error: failed to decode input'
        parser.exit(1, msg.format(prog_name))
