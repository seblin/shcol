PY=python

.PHONY: install clean test

install:
	$(PY) setup.py install

clean:
	rm -rf build/ dist/ MANIFEST
	find . -name '*.pyc' -exec rm -f {} +

test:
	$(PY) -m unittest discover testsuite
