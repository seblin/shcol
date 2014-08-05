shcol - A shell columnizer
--------------------------

``shcol`` is a shell columnizer that works in a similar way as the Unix-tool
``ls`` does when rendering directory contents.

Some examples:

```python
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
```

``shcol`` can also columnize the names of a Python-object:

```python
>>> shcol.print_attrs(shcol)
__author__    config    helpers      __package__       print_columnized_mapping
__builtins__  core      highlevel    __path__          print_filenames
cli           __doc__   __license__  print_attrs       __version__
columnize     __file__  __name__     print_columnized
>>> shcol.print_attrs(shcol, spacing=5)
__author__       core          __license__     print_columnized
__builtins__     __doc__       __name__        print_columnized_mapping
cli              __file__      __package__     print_filenames
columnize        helpers       __path__        __version__
config           highlevel     print_attrs
```

Note that the ``spacing``-parameter as shown above works with all kinds of
``print_*``-functions in ``shcol``.

You can also tell a ``print_*``-function to use a specific line width for
its output:

```python
>>> shcol.print_attrs(shcol, spacing=5, line_width=60)
__author__       __file__        print_attrs
__builtins__     helpers         print_columnized
cli              highlevel       print_columnized_mapping
columnize        __license__     print_filenames
config           __name__        __version__
core             __package__
__doc__          __path__
```

Note that by default the terminal's width is used as the line width.

And of course, you can columnize arbitrary names with ``shcol``:

```python
>>> shcol.print_columnized(['foo', 'bar', 'baz'], spacing=7)
foo       bar       baz
>>> shcol.print_columnized(['foo', 'bar', 'baz'], spacing=7, sort_items=True)
bar       baz       foo
```

The following example demonstrates that sorting is locale-aware. Note the
German umlaut in it. Hint: You need German as your default locale setting
to reproduce that in your Python interpreter:

```python
>>> shcol.print_columnized(['foo', 'bär', 'baz'], sort_items=True)
bär  baz  foo
```

You can see that ``shcol`` handles Unicode-characters as you would expect it.

In case you need the raw columnized string you can get that directly:

```python
>>> shcol.columnize(['foo', 'bär', 'baz'], sort_items=True)  # on Python 2.7
u'b\xe4r  baz  foo'
>>> shcol.columnize(['foo', 'bär', 'baz'], sort_items=True)  # on Python 3.x
'bär  baz  foo'
```


Command-line interface
----------------------

``shcol``s core functionality is also available from the command-line. Just run
the command ``shcol --help`` after installation to learn more about that.


How to install
--------------

To get the latest stable release (currently ``shcol 0.1`` from 2013-11-05):
``pip install shcol``.

To get the latest state of development (currently ``shcol 0.2-dev``):
``pip install git+git://github.com/seblin/shcol.git``.

Please note that all ``print_*``-functions as shown in the examples above will
only work with ``shcol 0.2``. So you currently will need the development version
if you want to use these functions. That version actually just needs more tests
and some more docstrings to be released, though it is pretty stable right now.
If you don't want the development version to be installed you can still pass the
contents to be rendered to ``shcol.columnize()`` by hand.


Additional notes
----------------

``shcol`` has its focus on usability and speed. Even large lists will be
rendered relatively fast (like ``shcol.print_filenames('/usr/bin')``).

Just give it a try if you like it and feel free to give some feedback. :-)
