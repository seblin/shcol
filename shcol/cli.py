from __future__ import print_function

import argparse
import shcol
import sys

__all__ = ['main']

def main(cmd_args):
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
        '-s', '--spacing', metavar='N', type=int, default=2,
        help='number of blanks between two columns (default: 2)'
    )
    parser.add_argument(
        '-w', '--width', metavar='N', type=int, default=80,
        help='maximal amount of characters per line (default: 80)'
    )
    parser.add_argument(
        '-S', '--sort', action='store_true', default=False,
        help='sort the items'
    )
    args = parser.parse_args(cmd_args[1:])
    items = args.items or [line.rstrip('\n') for line in sys.stdin]
    print(shcol.columnize(items, args.spacing, args.width, args.sort))
