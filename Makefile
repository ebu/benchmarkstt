.PHONY: docs test clean

test:
	pytest src --doctest-modules -vvv
	pytest --cov=src --cov-report html:htmlcov tests -vvv
	pycodestyle tests
	pycodestyle src

docs:
	cd docs/ && make clean html

clean:
	cd docs/ && make clean

