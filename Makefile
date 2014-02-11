.PHONY: install clean test

install:
	python setup.py install

clean:
	rm -rf build/ dist/ MANIFEST
	find . -name '*.pyc' -exec rm -f {} +

test:
	nosetests --verbosity=2