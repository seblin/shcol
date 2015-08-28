Introduction
============

What is shcol?
--------------

:program:`shcol` is a shell columnizer. It works in a similar way as the Unix
tool :program:`ls` does when rendering directory contents. :program:`shcol`
processes a given sequence of items and generates columnized output based on
these items. It has a command-line interface and a Python API.


Quick overview
--------------

Some simple examples running :program:`shcol` from the Windows PowerShell:

.. code-block:: powershell

   PS C:\> shcol foo bar baz  # Columnize a sequence of arguments
   foo  bar  baz
   PS C:\> shcol foo bar baz  --spacing=5  # Use more spacing
   foo     bar     baz
   PS C:\> shcol foo bar baz  --sort  # Sort the items
   bar  baz  foo
   PS C:\> echo foo bar baz | shcol  # Read items from a pipe
   foo  bar  baz

Read the chapter :doc:`cli-api` to learn about more details.

The following examples shall give a first impression about using the Python API:

.. code-block:: pycon

   >>> import shcol
   >>> shcol.print_columnized(['foo', 'bar', 'baz'])
   foo  bar  baz
   >>> shcol.print_columnized(['foo', 'bar', 'baz'], spacing=5)
   foo     bar     baz
   >>> shcol.print_columnized(['foo', 'bar', 'baz'], sort_items=True)
   bar  baz  foo
   >>> shcol.print_columnized(range(15), line_width=10)
   0  5  10
   1  6  11
   2  7  12
   3  8  13
   4  9  14
   >>> shcol.print_filenames(spacing=5, line_width=42)
   DLLs            NEWS.txt        share
   include         python.exe      tcl
   Lib             pythonw.exe     Tools
   libs            README.txt
   LICENSE.txt     Scripts
   >>> shcol.print_filenames('*.txt')
   LICENSE.txt  NEWS.txt  README.txt
   >>> import os
   >>> shcol.print_columnized(os.environ, pattern='PROG*', sort_items=True)
   PROGRAMDATA        C:\ProgramData
   PROGRAMFILES       C:\Program Files (x86)
   PROGRAMFILES(X86)  C:\Program Files (x86)
   PROGRAMW6432       C:\Program Files
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

:program:`shcol` is released under the Simplified BSD license.

(See the project's :file:`LICENSE`-file for details.)