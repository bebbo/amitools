PYTHON = python

.PHONY: help test dev sdist bdist

help:
	@echo "test       run tests"
	@echo "dev        dev install"

test:
	$(PYTHON) setup.py test

dev:
	$(PYTHON) setup.py develop --user

sdist:
	$(PYTHON) setup.py sdist

bdist:
	$(PYTHON) setup.py bdist_wheel
