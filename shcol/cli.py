import argparse
import sys

from . import __version__
from .highlevel import print_columnized

__all__ = ['main']

class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, prog_name, version):
        self._version_string = '{} {}'.format(prog_name, version)
        argparse.ArgumentParser.__init__(
            self, prog=prog_name,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description='Generate columnized output for given string items.\n\n'
            'Examples:\n'
            'shcol -S foo bar baz\n'
            'dpkg --get-selections \'python3*\' | shcol -c0 -s4\n'
            
        )
        self.init_arguments()

    def init_arguments(self):
        self.add_argument(
            'items', nargs='*', metavar='item',
            help='an item to columnize\n'
                 '(read from stdin if item arguments are not present)'
        )
        self.add_argument(
            '-s', '--spacing', metavar='N', type=self.num, default=2,
            help='number of blanks between two columns (default: 2)'
        )
        self.add_argument(
            '-w', '--width', metavar='N', type=self.num,
            help='maximal amount of characters per line\n'
                 '(use terminal width by default)'
        )
        self.add_argument(
            '-S', '--sort', action='store_true', default=False,
            help='sort the items'
        )
        self.add_argument(
            '-c', '--column', metavar='N', type=self.num, dest='column_index',
            help='choose a specific column per line via an index value\n'
                 '(indices start at 0, column seperator is whitespace)'
        )
        self.add_argument(
            '-v', '--version', action='version', version=self._version_string
        )

    def num(self, s):
        number = int(s)
        if number < 0:
            raise ValueError('number must be non-negative')
        return number

    def parse_args(self, args=None, namespace=None):
        args = argparse.ArgumentParser.parse_args(self, args, namespace)
        if not args.items:
            try:
                args.items = self.read_lines(sys.stdin, args.column_index)
            except IndexError:
                msg = '{}: error: failed to fetch data for column at index {}'
                _exit_with_failure(msg.format(self.prog, args.column_index))
            except KeyboardInterrupt:
                _exit_with_failure()
        return args

    def read_lines(self, stream, column_index=None):
        lines = (line.rstrip('\n') for line in stream)
        if column_index is not None:
            lines = (line.split()[column_index] for line in lines)
        return list(lines)

def _exit_with_failure(msg=None):
    if msg is not None:
        sys.stderr.write(msg + '\n')
    sys.exit(1)

def main(cmd_args=None, prog_name='shcol'):
    args = ArgumentParser(prog_name, __version__).parse_args()
    try:
        print_columnized(args.items, args.spacing, args.width, args.sort)
    except UnicodeEncodeError:
        msg = '{}: error: this input could not be encoded'
        _exit_with_failure(msg.format(prog_name))
