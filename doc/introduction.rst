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

These examples show running :program:`shcol` from the Windows PowerShell:

.. code-block:: powershell

   PS C:\> shcol foo bar baz --spacing=5
   foo     bar     baz
   PS C:\> shcol foo foo bar bar baz --unique
   foo  bar  baz
   PS C:\> (ls Python27).name | shcol --sort --width=50
   DLLs     libs         python.exe   tcl
   Doc      LICENSE.txt  pythonw.exe  Tools
   include  man          README.txt   w9xpopen.exe
   Lib      NEWS.txt     Scripts
   PS C:\> echo "foo`tbar`tbaz`nspam`tham`teggs" | shcol --column=0
   foo  spam


:program:`shcol` from a Python shell:

.. code-block:: pycon

   >>> import os, shcol
   >>> shcol.print_columnized(['foo', 'bar', 'baz'], spacing=5)
   foo     bar     baz
   >>> shcol.print_columnized(['foo', 'foo', 'bar', 'bar', 'baz'], make_unique=True)
   foo  bar  baz
   >>> shcol.print_filenames('Python27', line_width=50)
   DLLs     libs         python.exe   tcl
   Doc      LICENSE.txt  pythonw.exe  Tools
   include  man          README.txt   w9xpopen.exe
   Lib      NEWS.txt     Scripts
   >>> shcol.print_columnized(range(15), line_width=10)
   0  5  10
   1  6  11
   2  7  12
   3  8  13
   4  9  14
   >>> shcol.print_columnized(os.environ, pattern='*PROG*', sort_items=True)
   COMMONPROGRAMFILES       C:\Program Files (x86)\Common Files
   COMMONPROGRAMFILES(X86)  C:\Program Files (x86)\Common Files
   COMMONPROGRAMW6432       C:\Program Files\Common Files
   PROGRAMDATA              C:\ProgramData
   PROGRAMFILES             C:\Program Files (x86)
   PROGRAMFILES(X86)        C:\Program Files (x86)
   PROGRAMW6432             C:\Program Files
   >>> shcol.print_attr_names(shcol, pattern='print*')
   print_attr_names  print_columnized  print_filenames


How to install
--------------

Use :command:`pip install shcol` to get the latest stable release. This
currently picks :program:`shcol 0.2` for you. Please note that a few features as
shown above are not supported by that version.

If you rather like to fetch the latest state of development then you may run
:command:`pip install git+git://github.com/seblin/shcol.git` instead.


Compatibility
-------------

:program:`shcol` is tested regularly against Python *2.7* and Python *3.4* and
does work with both versions. It should also work with older Python *3.x*
versions. Python versions older than *2.7* are not supported.

You should be able to run :program:`shcol` on Windows as well as on Linux. There
are no dependencies to 3rd party libraries beyond the Python standard library.


License
-------

:program:`shcol` is released under the Simplified BSD license.

(See the project's :file:`LICENSE`-file for details.)
