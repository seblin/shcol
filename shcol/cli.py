from __future__ import print_function

import argparse
import shcol
import sys

__all__ = ['main']

def main(cmd_args=None):
    parser = argparse.ArgumentParser(
        description='Generate columnized output for given string items.',
        version='shcol {}'.format(shcol.__version__)
    )
    item_help = (
        'an item to columnize\n'
        '(read from stdin if item arguments are not present)'
    )
    parser.add_argument('items', nargs='*', metavar='item', help=item_help)
    parser.add_argument(
        '-s', '--spacing', metavar='N', type=num, default=2,
        help='number of blanks between two columns (default: 2)'
    )
    parser.add_argument(
        '-w', '--width', metavar='N', type=num, default=80,
        help='maximal amount of characters per line (default: 80)'
    )
    parser.add_argument(
        '-S', '--sort', action='store_true', default=False,
        help='sort the items'
    )
    args = parser.parse_args(cmd_args)
    items = args.items or _read_lines(sys.stdin)
    print(shcol.columnize(items, args.spacing, args.width, args.sort))


def num(s):
    number = int(s)
    if number <= 0:
        raise argparse.ArgumentError('number must be non-negative')
    return number

def _read_lines(stream):
    for line in stream:
        yield line.rstrip('\n')
