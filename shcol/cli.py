from __future__ import print_function

import argparse
import shcol

__all__ = ['main']

def main(cmd_args):
    parser = argparse.ArgumentParser(
        description='Generate columnized output for given string items.'
    )
    parser.add_argument('items', nargs='+', help='an item to columnize')
    parser.add_argument(
        '-s', '--spacing', metavar='NUM', type=int, default=2,
        help='number of blank characters between two columns'
    )
    args = parser.parse_args(cmd_args[1:])

    print(shcol.columnize(args.items, args.spacing))
