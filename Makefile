PYTHON=python
NOSETESTS=nosetests

.PHONY: install clean test test_verbose

install:
	$(PYTHON) setup.py install

clean:
	rm -rf build/ dist/ MANIFEST
	find . -name '*.pyc' -exec rm -f {} +

test:
	$(NOSETESTS)

test_verbose:
	$(NOSETESTS) --verbosity=2

