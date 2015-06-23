shcol - Documentation
=====================

What is shcol?
--------------

``shcol`` is a shell columnizer. It works in a similar way as the Unix-tool
``ls`` does when rendering directory contents. ``shcol`` processes a given
sequence of items and generates columnized output based on these items. It
has a command-line interface and a Python API.


Quick overview
--------------

Some simple examples running ``shcol`` from the Windows PowerShell:

.. code-block:: powershell

   PS C:\> shcol foo bar baz
   foo  bar  baz
   PS C:\> shcol --spacing=5 foo bar baz
   foo     bar     baz
   PS C:\> shcol --sort foo bar baz
   bar  baz  foo
   PS C:\> echo foo bar foo baz bar bar foo | shcol --sort --unique
   bar  baz  foo
   PS C:\> shcol --width=50 AAAAAAAA BBBBBBBBB CCCCCCCCCC DDDDDDDDDDDD EEEEEEEE
   AAAAAAAA   CCCCCCCCCC    EEEEEEEE
   BBBBBBBBB  DDDDDDDDDDDD
   PS C:\> shcol -w50 -s5 AAAAAAAA BBBBBBBBB CCCCCCCCCC DDDDDDDDDDDD EEEEEEEE
   AAAAAAAA      CCCCCCCCCC       EEEEEEEE
   BBBBBBBBB     DDDDDDDDDDDD


And here are some examples on how to use the Python API:

.. code-block:: pycon

   >>> import shcol
   >>> shcol.print_columnized(['foo', 'bar', 'baz'])
   foo  bar  baz
   >>> shcol.print_columnized(['foo', 'bar', 'baz'], spacing=5)
   foo     bar     baz
   >>> shcol.print_columnized(['foo', 'bar', 'baz'], sort_items=True)
   bar  baz  foo
   >>> items = ['foo', 'bar', 'foo', 'baz', 'bar', 'bar', 'foo']
   >>> shcol.print_columnized(items, sort_items=True, make_unique=True)
   bar  baz  foo
   >>> items = ['AAAAAAAA', 'BBBBBBBBB', 'CCCCCCCCCC', 'DDDDDDDDDDDD', 'EEEEEEEE']
   >>> shcol.print_columnized(items, line_width=50)
   AAAAAAAA   CCCCCCCCCC    EEEEEEEE
   BBBBBBBBB  DDDDDDDDDDDD
   >>> shcol.print_columnized(items, line_width=50, spacing=5)
   AAAAAAAA      CCCCCCCCCC       EEEEEEEE
   BBBBBBBBB     DDDDDDDDDDDD


The given sequence is not restricted to consist of strings:

.. code-block:: pycon

   >>> import shcol
   >>> shcol.print_columnized(range(15), line_width=10)
   0  5  10
   1  6  11
   2  7  12
   3  8  13
   4  9  14


``shcol`` is even able to render dictionaries:

.. code-block:: pycon

   >>> import os, shcol
   >>> shcol.print_columnized(os.environ, pattern='PROG*', sort_items=True)
   PROGRAMDATA        C:\ProgramData
   PROGRAMFILES       C:\Program Files (x86)
   PROGRAMFILES(X86)  C:\Program Files (x86)
   PROGRAMW6432       C:\Program Files


Globbing files is also supported:

.. code-block:: pycon

   >>> import os, shcol
   >>> os.chdir(os.path.dirname(shcol.__file__))
   >>> shcol.print_filenames('*.py', line_width=40)
   __init__.py  cli.py     core.py
   __main__.py  config.py  highlevel.py


Want to have a neat look on an object's attributes? Then you can do this:

.. code-block:: pycon

   >>> import shcol
   >>> shcol.print_attr_names(shcol, line_width=60)
   __author__    __loader__   cli        print_attr_names
   __builtins__  __name__     columnize  print_columnized
   __cached__    __package__  config     print_filenames
   __doc__       __path__     core
   __file__      __spec__     helpers
   __license__   __version__  highlevel
   >>> shcol.print_attr_names(shcol, pattern='print*')
   print_attr_names  print_columnized  print_filenames


How to install
--------------

Use ``pip install shcol`` to get the latest stable release. This currently picks
``shcol 0.2`` for you. Please note that a few features as shown above are *not*
supported by that version.

If you rather like to fetch the latest state of development then you may run
``pip install git+git://github.com/seblin/shcol.git`` instead.


License
-------

``shcol`` is released under the Simplified BSD license.

(See the project's ``LICENSE``-file for details.)
