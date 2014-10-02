# Copyright (c) 2013-2014, Sebastian Linke

# Released under the Simplified BSD license
# (see LICENSE file for details).

PY=python

.PHONY: install clean test

install:
	$(PY) setup.py install

clean:
	rm -rf build/ dist/ MANIFEST
	find . -name '*.pyc' -exec rm -f {} +

test:
	$(PY) -m unittest discover testsuite
