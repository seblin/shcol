PYTHON=python
NOSETESTS=nosetests

.PHONY: install clean test

install:
	$(PYTHON) setup.py install

clean:
	rm -rf build/ dist/ MANIFEST
	find . -name '*.pyc' -exec rm -f {} +

test:
	$(NOSETESTS) --verbosity=2
