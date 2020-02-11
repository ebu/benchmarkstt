.PHONY: docs test clean pypi

test:
	python -m pytest src --doctest-modules -vvv
	PYTHONPATH="./src/" python -m pytest --cov=./src --cov-report html:htmlcov ./tests -vvv
	python -m pycodestyle tests
	python -m pycodestyle src

testcoverage:
	PYTHONPATH="./src/" python -m pytest --cov=./src tests/

docs:
	cd docs/ && make clean html

setupdocs: setuptools
	python -m pip install -r docs/requirements.txt

dev: setuptools
	python -m pip install '.[test]'

clean:
	cd docs/ && make clean

setuptools:
	python -m pip install --upgrade setuptools wheel

pypi: setuptools test
	python setup.py sdist bdist_wheel
	python -m pip install --user --upgrade twine
	python -m twine upload dist/*
