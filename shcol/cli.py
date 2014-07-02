import argparse
import sys

from . import __version__
from .config import SPACING
from .helpers import exit_with_failure, num, read_lines
from .highlevel import print_columnized

__all__ = ['main']

class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, prog_name, version):
        self._version_string = '{} {}'.format(prog_name, version)
        argparse.ArgumentParser.__init__(
            self, prog=prog_name, formatter_class=argparse.RawTextHelpFormatter,
            description='Generate columnized output for given string items.\n\n'
            'Examples (on a Debian system):\n'
            '\n'
            'shcol -S foo bar baz\n'
            '(shcol -S -c0) < /proc/modules\n'
            'dpkg --get-selections \'python3*\' | shcol -c0 -s4'
        )
        self.init_arguments()

    def init_arguments(self):
        self.add_argument(
            'items', nargs='*', metavar='item',
            help='an item to columnize\n'
                 '(read from stdin if item arguments are not present)'
        )
        self.add_argument(
            '-s', '--spacing', metavar='N', type=num, default=SPACING,
            help='number of blanks between two columns (default: {})'
                 .format(SPACING)
        )
        self.add_argument(
            '-w', '--width', metavar='N', type=num,
            help='maximal amount of characters per line\n'
                 '(use terminal width by default)'
        )
        self.add_argument(
            '-S', '--sort', action='store_true', default=False,
            help='sort the items'
        )
        self.add_argument(
            '-c', '--column', metavar='N', type=num, dest='column_index',
            help='choose a specific column per line via an index value\n'
                 '(indices start at 0, column seperator is whitespace)'
        )
        self.add_argument(
            '-v', '--version', action='version', version=self._version_string
        )

    def parse_args(self, args=None, namespace=None):
        args = argparse.ArgumentParser.parse_args(self, args, namespace)
        if not args.items:
            try:
                args.items = list(read_lines(sys.stdin, args.column_index))
            except IndexError:
                msg = '{}: error: failed to fetch data for column at index {}'
                exit_with_failure(msg.format(self.prog, args.column_index))
            except KeyboardInterrupt:
                exit_with_failure()
        return args


def main(cmd_args=None, prog_name='shcol', version=None):
    if version is None:
        version = __version__
    args = ArgumentParser(prog_name, version).parse_args()
    try:
        print_columnized(args.items, args.spacing, args.width, args.sort)
    except UnicodeEncodeError:
        msg = '{}: error: this input could not be encoded'
        _exit_with_failure(msg.format(prog_name))
