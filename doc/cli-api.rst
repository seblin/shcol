Command-line interface API
==========================

Passing items
-------------

When running from the command-line there are two ways to feed the
:program:`shcol` command with items: You can either give it a sequence of
arguments representing the items (e.g. ``shcol foo bar baz``) or you pass the
items through its standard input stream.

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

To change the *spacing* just use the ``-s`` (long form: ``--spacing``) option.
If you want the columnized output of the previously shown example to include 5
space characters then you would do this:

.. code-block:: powershell

   PS C:\> (ps w*).name | shcol -s5
   wininit     winlogon     winpty-agent     wlanext     wmpnetwk     WUDFHost

Or more verbosely:

.. code-block:: powershell

   PS C:\> (ps w*).name | shcol --spacing=5
   wininit     winlogon     winpty-agent     wlanext     wmpnetwk     WUDFHost

For changing the *line width* you make use of the ``-w`` (long form:
``--width``) option. This shows an example for a line width of 50 characters:

.. code-block:: powershell

   PS C:\> (ps w*).name | shcol -w50
   wininit   winpty-agent  wmpnetwk
   winlogon  wlanext       WUDFHost
   PS C:\> (ps w*).name | shcol --width=50
   wininit   winpty-agent  wmpnetwk
   winlogon  wlanext       WUDFHost


Sorting the items
-----------------

:program:`shcol` is able to sort the given items before columnizing them. This
sorting will be locale-dependent on most systems. It is based on the system's
default locale settings.

To enable sorting you use the ``-S`` (long form: ``--sort``) option.

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
columnized output then the ``-U`` (long form: ``--unique``) option is a good way
to deal with that.

If this option is enabled then :program:`shcol` will ignore subsequent
occurrences of an item that already has been processed.

The effect when using that option is illustrated by the following example:

.. code-block:: powershell

   PS C:\> shcol foo bar foo baz bar baz foo -U
   foo  bar  baz
   PS C:\> shcol foo bar foo baz bar baz foo --unique
   foo  bar  baz
