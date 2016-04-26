# -*- coding: utf-8 -*-
# Copyright (c) 2013-2016, Sebastian Linke

# Released under the Simplified BSD license
# (see LICENSE file for details).

import sys

# Fail as early as possible, since some imports may cause errors on old versions
if sys.version_info < (2, 7):
    sys.exit('ERROR: Python interpreter\'s version must be 2.7 or higher\n')

from distutils.core import setup
import shcol

def main():
    setup(
        name='shcol',
        version=shcol.__version__,
        description='A shell columnizer',
        long_description=shcol.__doc__,
        author=shcol.__author__,
        author_email='Seb_Linke@arcor.de',
        url='https://github.com/seblin/shcol',
        packages=['shcol', 'shcol.helpers'],
        scripts=[shcol.config.STARTER],
        license=shcol.__license__,
        platforms = 'any',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: BSD License',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Topic :: System :: Shells',
        ],
    )

if __name__ == '__main__':
    main()
