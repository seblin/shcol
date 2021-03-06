Command-line interface
======================

Passing items
-------------

When running from the command-line there are two ways to feed the
:program:`shcol` command with items: You can either give it a sequence of
arguments representing the items (e.g. :command:`shcol foo bar baz`) or you pass
the items through its standard input stream.

The latter form makes it easy to combine :program:`shcol` with other shell
commands. On Windows PowerShell, for example, you could columnize the names of
all running processes starting with "w" like this:

.. code-block:: powershell

   PS C:\> (ps w*).name | shcol
   wininit  winlogon  winpty-agent  wlanext  wmpnetwk  WUDFHost


Configuring the output
----------------------

By default, :program:`shcol` will put 2 space characters between the items.
Also, it is able to detect the terminal's line width automatically in most cases
in order to use that width for columnizing. But of course, you can change the
spacing as well as the line width to be used.

To change the *spacing* just use the :option:`-s` (long form:
:option:`--spacing`) option. If you want the columnized output of the previously
shown example to include 5 space characters then you would do this:

.. code-block:: powershell

   PS C:\> (ps w*).name | shcol -s5
   wininit     winlogon     winpty-agent     wlanext     wmpnetwk     WUDFHost

Or more verbosely:

.. code-block:: powershell

   PS C:\> (ps w*).name | shcol --spacing=5
   wininit     winlogon     winpty-agent     wlanext     wmpnetwk     WUDFHost

For changing the *line width* you make use of the :option:`-w` (long form:
:option:`--width`) option. This shows an example for a line width of 50
characters:

.. code-block:: powershell

   PS C:\> (ps w*).name | shcol -w50
   wininit   winpty-agent  wmpnetwk
   winlogon  wlanext       WUDFHost
   PS C:\> (ps w*).name | shcol --width=50
   wininit   winpty-agent  wmpnetwk
   winlogon  wlanext       WUDFHost


Using an extra separator
------------------------

If you need to add an additional separator between the columns then this can be
done by using the :option:`-e` (long form: :option:`--extra-sep`) option:

.. code-block:: powershell

   PS C:\> (ps w*).name | shcol -e"-"
   wininit - winlogon - winpty-agent - WUDFHost
   PS C:\> (ps w*).name | shcol --extra-sep="-"
   wininit - winlogon - winpty-agent - WUDFHost
   PS C:\> (ps w*).name | shcol --extra-sep="-" --width=25
   wininit  - winpty-agent
   winlogon - WUDFHost

*(New feature in development version - not yet released.)*


Selecting a specific column
---------------------------

If your input consists of lines that represent multiple columns then you
probably want to choose a specific column to be processed by :program:`shcol`.
To achieve this you can use the :option:`-c` (long form: :option:`--column`)
option.

:program:`shcol` interprets a column as a sequence of non-whitespace characters.
Column counting starts with 0 like indices do in most programming languages.

The following snippet shows how to use this option:

.. code-block:: powershell

   PS C:\> echo foo`tXXX bar`tYYY baz`tZZZ
   foo     XXX
   bar     YYY
   baz     ZZZ
   PS C:\> echo foo`tXXX bar`tYYY baz`tZZZ | shcol -c0
   foo  bar  baz
   PS C:\> echo foo`tXXX bar`tYYY baz`tZZZ | shcol --column=1
   XXX  YYY  ZZZ


Using patterns
--------------

Sometimes you want to filter your input according to specific criteria. For
this, :program:`shcol` supports filtering by wildcards (namely: `?` and
`*`). You make use of filtering by passing a pattern to the :option:`-F` (long
form: :option:`--filter`) option.

Filtering can be done like this:

.. code-block:: powershell

   PS C:\> echo foo bar baz | shcol -F"f*"
   foo
   PS C:\> echo foo bar baz | shcol -F"b*"
   bar  baz
   PS C:\> echo foo bar baz | shcol -F"*a*"
   bar  baz
   PS C:\> echo foo bar baz | shcol -F"*r"
   bar
   PS C:\> echo foo bar baz | shcol -F"ba?"
   bar  baz
   PS C:\> echo foo bar baz | shcol --filter="?a?"
   bar  baz


Sorting the items
-----------------

:program:`shcol` is able to sort the given items before columnizing them. This
sorting will be locale-dependent on most systems. It is based on the system's
default locale settings. To enable sorting you use the :option:`-S` (long form:
:option:`--sort`) option.

The following example shows sorting including an item with a German Umlaut and
with German set as the default locale:

.. code-block:: powershell

   PS C:\> shcol foo bär baz -S
   bär  baz  foo
   PS C:\> shcol foo bär baz --sort
   bär  baz  foo


Making items unique
-------------------

If your input contains duplicates and you don't want to have duplicates in your
columnized output then the :option:`-U` (long form: :option:`--unique`) option
is a good way to deal with that.

If this option is enabled then :program:`shcol` will ignore subsequent
occurrences of an item that already has been processed.

The effect when using that option is illustrated by the following example:

.. code-block:: powershell

   PS C:\> shcol foo bar foo baz bar baz foo -U
   foo  bar  baz
   PS C:\> shcol foo bar foo baz bar baz foo --unique
   foo  bar  baz
