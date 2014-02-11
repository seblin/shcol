from __future__ import print_function
from .core import columnize
import os

__all__ = ['show_attrs', 'show_files']

def show_attrs(obj):
    print(columnize(dir(obj), sort_items=True))

def show_files(path='.'):
    print(columnize(os.listdir(path), sort_items=True))
