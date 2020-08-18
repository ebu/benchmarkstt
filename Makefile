.PHONY: docs test clean pypi env

PYTHON:=$(shell test -e env/bin/activate && echo "env/bin/python" || echo "python3")

env:
	echo "Using $(shell exec $(PYTHON) --version): $(PYTHON)"
	$(PYTHON) -m ensurepip

test: env lint
	$(PYTHON) -m pytest src --doctest-modules -vvv
	PYTHONPATH="./src/" $(PYTHON) -m pytest --cov=./src --cov-report html:htmlcov ./tests -vvv

lint:
	$(PYTHON) -m pycodestyle tests
	$(PYTHON) -m pycodestyle src

testcoverage: env
	PYTHONPATH="./src/" $(PYTHON) -m pytest --cov=./src tests/

docs: setupdocs clean uml
	cd docs/ && make html

setupdocs: env
	$(PYTHON) -m pip install -r docs/requirements.txt

dev: env setuptools
	$(PYTHON) -m pip install -e '.[test]'

uml: env cleanuml
	PYTHONPATH="./src/" $(PYTHON) src/benchmarkstt/_uml.py

clean:
	cd docs/ && make clean

cleanuml:
	for e in svg puml; do for f in docs/_static/uml/*."$$e"; do [ -e "$$f" ] && rm docs/_static/uml/*."$$e"; break; done; done

setuptools: env
	$(PYTHON) -m pip install --upgrade setuptools wheel

pypi: env setuptools test
	$(PYTHON) setup.py sdist bdist_wheel
	$(PYTHON) -m pip install --user --upgrade twine
	$(PYTHON) -m twine upload dist/*

