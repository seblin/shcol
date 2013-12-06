from __future__ import print_function

import argparse
import shcol

__all__ = ['main']

def main(cmd_args):
    parser = argparse.ArgumentParser(
        description='Generate columnized output for given string items.',
        version='shcol {}'.format(shcol.__version__)
    )
    parser.add_argument('items', nargs='+', help='an item to columnize')
    parser.add_argument(
        '-s', '--spacing', metavar='N', type=int, default=2,
        help='number of blank characters between two columns'
    )
    parser.add_argument(
        '-w', '--width', metavar='N', type=int, default=80,
        help='maximal amount of characters per line'
    )
    
    args = parser.parse_args(cmd_args[1:])

    print(shcol.columnize(args.items, args.spacing, args.width))
