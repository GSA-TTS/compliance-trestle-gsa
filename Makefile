# -*- mode:makefile; config:utf-8 -*-

develop:
	python -m pip install -e .[dev] --upgrade --upgrade-strategy eager --

test:
	python -m pytest -vvvv --exitfirst -n auto

code-lint:
	flake8

install:
	python -m pip install --upgrade pip build twine
	python -m pip install . --upgrade --upgrade-strategy eager

package: install
	python -m build

release:
	python -m twine upload dist/*

clean:
	rm -rf build/
	rm -rf dist/
