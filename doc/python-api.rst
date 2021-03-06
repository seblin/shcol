Python API
==========

Input types
-----------

:program:`shcol` can columnize any item by simply relying on its string
representation. The following example from an interactive Python session will
illustrate that behavior:

.. code-block:: pycon

   >>> import shcol
   >>> shcol.print_columnized(['spam', 0, 1.23, shcol.print_columnized])
   spam  0  1.23  <function print_columnized at 0x039A8BB8>

Note that you are not restricted to use lists. You just need to pass an iterable
object that contains the items to columnize. So these things are possible, too:

.. code-block:: pycon

    >>> shcol.print_columnized('abcdefg')
    a  b  c  d  e  f  g
    >>> shcol.print_columnized(xrange(10))
    0  1  2  3  4  5  6  7  8  9
    >>> shcol.print_columnized(n for n in xrange(10) if n >= 5)
    5  6  7  8  9

:program:`shcol` is also able to columnize dictionaries:

.. code-block:: pycon

    >>> inventory = {'Apples': 100, 'Bananas': 200}
    >>> shcol.print_columnized(inventory)
    Apples   100
    Bananas  200


Changing spacing and line width
-------------------------------

You can pass your own settings for the spacing between each item and for the
output's line width.

To do this, just use the appropriated keyword arguments:

.. code-block:: pycon

    >>> shcol.print_columnized(xrange(10), spacing=4)
    0    1    2    3    4    5    6    7    8    9
    >>> shcol.print_columnized(xrange(10), line_width=15)
    0  2  4  6  8
    1  3  5  7  9


How to use an additional separator
----------------------------------

You maybe want to add an extra separator between the columns in some situations.
For this purpose, the :option:`extra_sep`-option was designed.

It takes a single character and can be used like this:

.. code-block:: pycon

   >>> shcol.print_columnized(xrange(10), extra_sep='|')
   0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
   >>> shcol.print_columnized(xrange(10), extra_sep='|', line_width=20)
   0 | 2 | 4 | 6 | 8
   1 | 3 | 5 | 7 | 9

*(New feature in development version - not yet released.)*


Filtering input
---------------

Sometimes you want to filter your input according to specific criteria. For
this, :program:`shcol` supports filtering by wildcards (namely: `?` and
`*`).

This is how to pass different patterns as a filter:

.. code-block:: pycon

    >>> items = ['foo', 'bar', 'baz']
    >>> shcol.print_columnized(items, pattern='f*')
    foo
    >>> shcol.print_columnized(items, pattern='b*')
    bar  baz
    >>> shcol.print_columnized(items, pattern='*a*')
    bar  baz
    >>> shcol.print_columnized(items, pattern='*r*')
    bar
    >>> shcol.print_columnized(items, pattern='ba?')
    bar  baz
    >>> shcol.print_columnized(items, pattern='?a?')
    bar  baz


How to sort
-----------

:program:`shcol` will do locale-dependent sorting via the :option:`sort_items`
keyword.

Sorting can be done like this:

.. code-block:: pycon

    >>> shcol.print_columnized(['spam', 'ham', 'eggs'], sort_items=True)
    eggs  ham  spam
    >>> shcol.print_columnized(['späm', 'häm', 'äggs'], sort_items=True)
    äggs  häm  späm

Please note that sorting items with non-ASCII characters will only work as
intended if your system's locale setting was set accordingly, i.e. in order to
sort German Umlauts as shown above you should set a german locale.


Eliminating duplicates
----------------------

If your input contains duplicates and you don't want to have duplicates in your
columnized output then the :option:`make_unique` keyword is a good way to deal
with that.

When this feature is enabled then :program:`shcol` will ignore subsequent
occurrences of an item that already has been processed.

The effect of using :option:`make_unique` is illustrated by the following
example:

.. code-block:: pycon

   >>> items = ['spam', 'ham', 'spam', 'eggs', 'ham', 'eggs', 'spam']
   >>> shcol.print_columnized(items, make_unique=True)
   spam  ham  eggs

Note that :option:`make_unique` preserves the original order of the given items.
This differs from calling the Python standard library's `set()`-constructor,
which makes no guarantees about the order of its result.


Printing directory contents
---------------------------

:program:`shcol` includes a function called `print_filenames()` in order to
print the content of a given path.

When called without arguments, it will print the filenames inside the current
directory. For example, this is the result on the author's Windows system when
the current directory is `C:\\Python27`:

.. code-block:: pycon

   >>> shcol.print_filenames()
   DLLs  include  libs         man       python.exe   README.txt  tcl    w9xpopen.exe
   Doc   Lib      LICENSE.txt  NEWS.txt  pythonw.exe  Scripts     Tools

The same effect can be achieved from `C:\\` when passing the directory name:

.. code-block:: pycon

   >>> shcol.print_filenames('Python27')
   DLLs  include  libs         man       python.exe   README.txt  tcl    w9xpopen.exe
   Doc   Lib      LICENSE.txt  NEWS.txt  pythonw.exe  Scripts     Tools

You may also pass wildcard characters (`*` and `?`) in order to make use of
shell globbing:

.. code-block:: pycon

   >>> shcol.print_filenames('Py*')
   pypy26  Python27  Python34
   >>> shcol.print_filenames('Py*2?')
   pypy26  Python27
   >>> shcol.print_filenames('Python27\*.txt')
   LICENSE.txt  NEWS.txt  README.txt

Note that `print_columnized()` is used under the hood to do the actual
columnizing, so all of its options (such as :option:`spacing`,
:option:`line_width`, ...) are available as well:

.. code-block:: pycon

   >>> shcol.print_filenames('Python27', spacing=5, line_width=50)
   DLLs        LICENSE.txt     README.txt
   Doc         man             Scripts
   include     NEWS.txt        tcl
   Lib         python.exe      Tools
   libs        pythonw.exe     w9xpopen.exe


The `print_sorted()`-shortcut
-----------------------------

For convenience, the idiom `print_columnized(items, sort_items=True)` can be
replaced with `print_sorted(items)`. As known from `print_filenames()`, all
additional options are passed to `print_columnized()` to be interpreted there.

The following examples show some use cases where this function is used to
inspect objects in a Python interpreter session:

.. code-block:: pycon

   >>> shcol.print_sorted(dir(shcol), line_width=50)
   __author__    __path__     helpers
   __builtins__  __version__  highlevel
   __doc__       cli          print_columnized
   __file__      columnize    print_filenames
   __license__   config       print_sorted
   __name__      core
   __package__   formatters
   >>> shcol.print_sorted(dir(shcol), pattern='print*')
   print_columnized  print_filenames  print_sorted
   >>> import os
   >>> shcol.print_sorted(os.environ, pattern='*PROG*')
   COMMONPROGRAMFILES       C:\Program Files (x86)\Common Files
   COMMONPROGRAMFILES(X86)  C:\Program Files (x86)\Common Files
   COMMONPROGRAMW6432       C:\Program Files\Common Files
   PROGRAMDATA              C:\ProgramData
   PROGRAMFILES             C:\Program Files (x86)
   PROGRAMFILES(X86)        C:\Program Files (x86)
   PROGRAMW6432             C:\Program Files