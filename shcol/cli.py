from __future__ import print_function

import argparse
import shcol
import sys

__all__ = ['main']

class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, prog_name, version):
        self._version_string = '{} {}'.format(prog_name, version)
        description = 'Generate columnized output for given string items.'
        argparse.ArgumentParser.__init__(
            self, prog=prog_name, description=description
        )
        self._add_arguments()

    def _add_arguments(self):
        item_help = (
            'an item to columnize\n'
            '(read from stdin if item arguments are not present)'
        )
        self.add_argument('items', nargs='*', metavar='item', help=item_help)
        self.add_argument(
            '-s', '--spacing', metavar='N', type=self.num, default=2,
            help='number of blanks between two columns (default: 2)'
        )
        self.add_argument(
            '-w', '--width', metavar='N', type=self.num, default=80,
            help='maximal amount of characters per line (default: 80)'
        )
        self.add_argument(
            '-S', '--sort', action='store_true', default=False,
            help='sort the items'
        )
        self.add_argument(
            '-c', '--column', metavar='N', type=self.num, dest='column_index',
            help='select a specific column via its index'
        )
        self.add_argument(
            '-v', '--version', action='version', version=self._version_string
        )

    def num(self, s):
        number = int(s)
        if number < 0:
            raise argparse.ArgumentError('number must be non-negative')
        return number

    def parse_args(self, args=None, namespace=None):
        args = argparse.ArgumentParser.parse_args(self, args, namespace)
        if not args.items:
            try:
                args.items = self._read_lines(sys.stdin, args.column_index)
            except IndexError:
                msg = 'unable to fetch data for column at index {}'
                self._fail(msg.format(args.column_index))
        return args

    def _read_lines(self, stream, column_index=None):
        lines = (line.rstrip('\n') for line in stream)
        if column_index is not None:
            lines = (line.split()[column_index] for line in lines)
        return list(lines)

    def _fail(self, msg, exit_code=1):
        error_msg = '{}: error: {}'.format(self.prog, msg)
        print(error_msg, file=sys.stderr)
        sys.exit(exit_code)


def main(cmd_args=None):
    args = ArgumentParser('shcol', shcol.__version__).parse_args()
    print(shcol.columnize(args.items, args.spacing, args.width, args.sort))
