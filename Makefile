.PHONY: install clean test

install:
	python setup.py install

clean:
	rm -rf build/ dist/ MANIFEST
	find . -name '__pycache__' -exec rm -f {} +
	find . -name '*.pyc' -exec rm -f {} +

test:
	python test/test_core.py
