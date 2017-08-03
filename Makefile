PYTHON = python

.PHONY: help test dev

help:
	@echo "test       run tests"
	@echo "dev        dev install"

test:
	$(PYTHON) setup.py test

dev:
	$(PYTHON) setup.py develop --user
