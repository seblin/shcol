from __future__ import print_function
from .core import columnize
import os

__all__ = ['show_attrs', 'show_files']

def show_attrs(obj):
    print(columnize(dir(obj), sort_items=True))

def show_files(path='.', hide_dotted=False):
    filenames = os.listdir(path)
    if hide_dotted:
        filenames = [fn for fn in filenames if not fn.startswith('.')]
    print(columnize(filenames, sort_items=True))
