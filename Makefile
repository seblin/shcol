PY=python
NOSE=nosetests

.PHONY: install clean test test_verbose

install:
	$(PY) setup.py install

clean:
	rm -rf build/ dist/ MANIFEST
	find . -name '*.pyc' -exec rm -f {} +

test:
	$(NOSE)

test_verbose:
	$(NOSE) --verbosity=2

