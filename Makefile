.PHONY: docs test clean pypi env

PYTHON=$(shell test -e env/bin/activate && echo "env/bin/python" || echo "python3")

env:
	test -e env/bin/activate && source env/bin/activate
	echo "Using $(shell exec $(PYTHON) --version): $(PYTHON)"

test: env lint
	$(PYTHON) -m pytest src --doctest-modules -vvv
	PYTHONPATH="./src/" $(PYTHON) -m pytest --cov=./src --cov-report html:htmlcov ./tests -vvv

lint:
	$(PYTHON) -m pycodestyle tests
	$(PYTHON) -m pycodestyle src

testcoverage: env
	PYTHONPATH="./src/" $(PYTHON) -m pytest --cov=./src tests/

docs: setupdocs
	cd docs/ && make clean html

setupdocs: env
	$(PYTHON) -m pip install -r docs/requirements.txt

dev: env setuptools
	$(PYTHON) -m pip install -e '.[test]'

uml: env
	PYTHONPATH="./src/" $(PYTHON) src/benchmarkstt/uml.py

clean:
	cd docs/ && make clean

setuptools: env
	$(PYTHON) -m pip install --upgrade setuptools wheel

pypi: env setuptools test
	$(PYTHON) setup.py sdist bdist_wheel
	$(PYTHON) -m pip install --user --upgrade twine
	$(PYTHON) -m twine upload dist/*
