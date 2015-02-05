# Copyright (c) 2013-2015, Sebastian Linke

# Released under the Simplified BSD license
# (see LICENSE file for details).

PY=python

.PHONY: install clean test upload

install:
	$(PY) setup.py install

clean:
	rm -rf build/ dist/ MANIFEST
	find . -name '*.pyc' -exec rm -f {} +

test:
	$(PY) -m unittest discover testsuite

upload:
	$(PY) setup.py sdist upload
