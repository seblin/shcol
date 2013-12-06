#!/usr/bin/env python
from distutils.core import setup
import shcol

setup(
    name='shcol',
    version=shcol.__version__,
    description='A shell columnizer',
    long_description=shcol.__doc__,
    author=shcol.__author__,
    author_email='Seb_Linke@arcor.de',
    url='https://github.com/seblin/shcol',
    packages=['shcol'],
    scripts=['bin/shcol'],
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
        'Topic :: System :: Shells',
    ],
)
