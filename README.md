shcol - A shell columnizer
--------------------------

``shcol`` generates columnized output for given string items.

Example:

```python
>>> import shcol
>>> items = dir(shcol)
>>> print shcol.columnize(items)
ColumnWidthCalculator  __all__       __name__     functools
Formatter              __builtins__  __package__  locale
LineProperties         __doc__       collections  os
_DefaultLocale         __file__      columnize    unicode_literals
```

The same will work for file listings:

```python
>>> import os
>>> print shcol.columnize(os.listdir('/'))
selinux  bin   etc             lib64  media       usr         sbin  proc
run      root  initrd.img.old  sys    tmp         initrd.img  lib   dev
home     boot  srv             var    lost+found  vmlinuz     opt   mnt
```

For convenience ``shcol`` can sort the output for you:

```python
>>> print shcol.columnize(os.listdir('/'), sort_items=True)
bin   etc         initrd.img.old  lost+found  opt   run      srv  usr
boot  home        lib             media       proc  sbin     sys  var
dev   initrd.img  lib64           mnt         root  selinux  tmp  vmlinuz
```

It even handles input containing non-ascii strings correctly:

```python
>>> home_path = os.path.expanduser('~')
>>> print shcol.columnize(os.listdir(home_path), sort_items=True)
.adobe                      .gnome2_private   .pip
.alsaplayer                 .gnupg            .pki
Arbeitsfläche               .gphoto           .profile
backup                      .gstreamer-0.10   prog
.bash_history               .gtk-bookmarks    .psensor
.bash_logout                .hardinfo         .pulse
bewerbung                   .ICEauthority     .pulse-cookie
Bilder                      .IdeaIC12         PyBitmessage
bin                         .idlerc           .pypirc
cache                       .java             .pyxbld
.cache                      .jdownloader      .sane
C:\nppdf32Log\debuglog.txt  .jython-cache     .spe
.config                     .kde              spiele
.dbus                       .lesshst          .ssh
.dmrc                       .linuxmint        .subversion
Dokumente                   .local            .thumbnails
Downloads                   .macromedia       .thunderbird
dwhelper                    .mozilla          tor-browser_de
fh                          Musik             Videos
.gconf                      .mysql_history    Vorlagen
geditpycompletion           .nano_history     .wine
.gftp                       .nbi              .Xauthority
.gimp-2.8                   .netbeans         .xsession-errors
.gitconfig                  netbeans-7.4      .zcompdump
.git-credential-cache       NetBeansProjects  zip
.gitk                       notizen           .zsh_history
.gksu.lock                  .odbc.ini         .zshrc
glassfish-4.0               Öffentlich
.gnome2                     .pam_environment
```

That result should be pretty equivalent to what a call to ``ls -A ~`` on your
command-line would give you.

Additionally, you are free to change the spacing between columns:

```python
>>> print shcol.columnize(os.listdir('/'), spacing=4, sort_items=True)
bin     home              lib64         opt     sbin       tmp
boot    initrd.img        lost+found    proc    selinux    usr
dev     initrd.img.old    media         root    srv        var
etc     lib               mnt           run     sys        vmlinuz
```

...or to change the line width:

```python
>>> print shcol.columnize(os.listdir('/'), max_line_width=50, sort_items=True)
bin   initrd.img      media  run      tmp
boot  initrd.img.old  mnt    sbin     usr
dev   lib             opt    selinux  var
etc   lib64           proc   srv      vmlinuz
home  lost+found      root   sys
```

(Note that future versions of ``shcol`` will try to use an appropriate line
width on their own.)

``shcol`` has its focus on speed, features and usability, though it is in an
early development state. See the source code for details on what ``shcol`` is
currently able to do for you.

How to install
--------------

The preferred way is to use the simple command: ``pip install shcol``.
