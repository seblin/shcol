# -*- coding: utf-8 -*-
# Copyright (c) 2013-2016, Sebastian Linke

# Released under the Simplified BSD license
# (see LICENSE file for details).

"""
`shcol` is a shell columnizer that works in a similar way as the Unix-tool `ls`
does when rendering directory contents.

Some examples:

>>> import shcol
>>> shcol.print_filenames()  # print contents of current directory
bin    LICENSE   MANIFEST.in  setup.py  testsuite
build  Makefile  README.md    shcol
>>> shcol.print_filenames('testsuite')  # print contents of a subdirectory
test_cli.py   test_core.py   test_highlevel.py   test_script.py
test_cli.pyc  test_core.pyc  test_highlevel.pyc  test_script.pyc
>>> shcol.print_filenames('testsuite/*.py')  # only print `*.py`-files
testsuite/test_cli.py   testsuite/test_highlevel.py
testsuite/test_core.py  testsuite/test_script.py
>>> shcol.print_filenames('~/shcol', hide_dotted=False)  # like `ls -A ~/shcol`
bin    .git     Makefile     README.md  shcol
build  LICENSE  MANIFEST.in  setup.py   testsuite

`shcol` can also columnize the attribute names of a Python-object:

>>> shcol.print_sorted(shcol)
__author__    config    helpers      __package__       print_columnized_mapping
__builtins__  core      highlevel    __path__          print_filenames
cli           __doc__   __license__  print_attrs       __version__
columnize     __file__  __name__     print_columnized
>>> shcol.print_sorted(shcol, spacing=5)
__author__       core          __license__     print_columnized
__builtins__     __doc__       __name__        print_columnized_mapping
cli              __file__      __package__     print_filenames
columnize        helpers       __path__        __version__
config           highlevel     print_attrs

Note that the `spacing`-parameter as shown above works with all kinds of
`print_*`-functions in `shcol`.

You can also tell a `print_*`-function to use a specific line width for
its output:

>>> shcol.print_sorted(shcol, spacing=5, line_width=60)
__author__       __file__        print_attrs
__builtins__     helpers         print_columnized
cli              highlevel       print_columnized_mapping
columnize        __license__     print_filenames
config           __name__        __version__
core             __package__
__doc__          __path__

Note that by default the terminal's width is used as the line width.

And of course, you can columnize arbitrary names with `shcol`:

>>> shcol.print_columnized(['foo', 'bar', 'baz'], spacing=7)
foo       bar       baz
>>> shcol.print_columnized(['foo', 'bar', 'baz'], spacing=7, sort_items=True)
bar       baz       foo

The following example demonstrates that sorting is locale-aware. Note the
German umlaut in it. Hint: You need German as your default locale setting
to reproduce that in your Python interpreter:

>>> shcol.print_columnized(['foo', 'bär', 'baz'], sort_items=True)
bär  baz  foo

You can see that `shcol` handles Unicode-characters as you would expect it.

In case you need the raw columnized string you can get that directly:

>>> shcol.columnize(['foo', 'bär', 'baz'], sort_items=True)  # on Python 2.7
u'b\\xe4r  baz  foo'
>>> shcol.columnize(['foo', 'bär', 'baz'], sort_items=True)  # on Python 3.x
'bär  baz  foo'

`shcol` has its focus on usability and speed. Even large lists will be
rendered relatively fast (like ``shcol.print_filenames('/usr/bin')``).

Just give it a try if you like it and feel free to give some feedback. :-)
"""

__author__ = 'Sebastian Linke'
__version__ = '0.3'
__license__ = 'Simplified BSD'

from . import cli
from .core import *
from .highlevel import *

if __name__ == '__main':
    cli.main()
