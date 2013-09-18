shcol - A shell columnizer
==========================

``shcol`` generates columnized output for given string items.

Example:

>>> import shcol
>>> items = dir(shcol)
>>> print shcol.columnize(items)
ColumnWidthCalculator  __all__       __name__     functools
Formatter              __builtins__  __package__  locale
LineProperties         __doc__       collections  os
_DefaultLocale         __file__      columnize    unicode_literals

The same will work for file listings:

>>> import os
>>> print shcol.columnize(os.listdir('/'))
selinux  bin   etc             lib64  media       usr         sbin  proc
run      root  initrd.img.old  sys    tmp         initrd.img  lib   dev
home     boot  srv             var    lost+found  vmlinuz     opt   mnt

For convenience ``shcol`` can sort the output for you:

>>> print shcol.columnize(os.listdir('/'), sort_items=True)
bin   etc         initrd.img.old  lost+found  opt   run      srv  usr
boot  home        lib             media       proc  sbin     sys  var
dev   initrd.img  lib64           mnt         root  selinux  tmp  vmlinuz

That result should be pretty equivalent to what a call to ``ls /`` on your
commandline would give you.

You are free to change the number of blank characters between these columns:

>>> print shcol.columnize(os.listdir('/'), spacing=4, sort_items=True)
bin     home              lib64         opt     sbin       tmp
boot    initrd.img        lost+found    proc    selinux    usr
dev     initrd.img.old    media         root    srv        var
etc     lib               mnt           run     sys        vmlinuz

``shcol`` has its focus on speed, features and usability, though it is in an
early development state. See the source code for details on what ``shcol`` is
currently able to do for you.
