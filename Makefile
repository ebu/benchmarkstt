.PHONY: docs test clean pypi

test:
	pytest src --doctest-modules -vvv
	pytest --cov=src --cov-report html:htmlcov tests -vvv
	pycodestyle tests
	pycodestyle src

docs:
	cd docs/ && make clean html

clean:
	cd docs/ && make clean

pypi: test
	python3 -m pip install --user --upgrade setuptools wheel
	python3 setup.py sdist bdist_wheel
	python3 -m pip install --user --upgrade twine
	python3 -m twine upload dist/*
