from __future__ import print_function
from .core import columnize

__all__ = ['show_attrs']

def show_attrs(obj):
    print(columnize(dir(obj), sort_items=True))
